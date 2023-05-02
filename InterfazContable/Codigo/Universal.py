from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from datetime import datetime
from CRUD import *
import numpy as np 

def LlenarCampoCero(universal, nombreCampo, valor):

    universalCopia = universal.copy()
    i = 0
    while i < len(universalCopia):
        if pd.isna(universalCopia[nombreCampo][i]):
            universalCopia.loc[i, nombreCampo] = valor
        i = i + 1

    return universalCopia

def ListaMesesLetra():

    meses = pd.DataFrame()
    numeroMes = ['01', '02', '03', '04', '05', '06','07', '08', '09', '10', '11', '12']
    letraMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    meses['Numero Mes'] = numeroMes
    meses['Letra Mes'] = letraMes

    return meses

def RenombrarColumnas(universal, nombreNc, mes):

    universalCopia = universal.copy()
    i = 0
    while i < len(universalCopia.columns):
        if nombreNc == universalCopia.columns[i]:
            meses = ListaMesesLetra()
            j = 0
            while j < len(meses):
                if meses['Numero Mes'][j] == mes:
                    mes = meses['Letra Mes'][j]
                j = j + 1
            campo = nombreNc + " " + mes.upper()
            universalCopia = universalCopia.rename(columns={nombreNc:campo})    
        i = i + 1

    return universalCopia

def ObtenerFechaCorteAnterior():

    fechaActual = datetime.now()
    anio = fechaActual.strftime('%Y')
    mes = fechaActual.strftime('%m')
    anio = int(anio)
    mes = int(mes)

    if mes == 1:
        mes = 12
        anio = anio - 1
    else:
        mes = mes - 1
    if mes <= 9:
        mes = str(mes)
        mes = "0" + mes
    else:
        mes = str(mes)

    anio = str(anio)
    fechaCorte = anio + "-" + mes

    return fechaCorte

def ObtenerFechaActual():

    fecha = datetime.now()
    anio = fecha.strftime('%Y')
    mes = fecha.strftime('%m')
    fecha = anio + "-" + mes + "-" + "01"  

    return fecha

def ObtenerCarteraPorFecha(base,nombreColumna,fechaCorte):
    
    baseCopia = base.copy()

    i = 0
    while i < len(baseCopia):
        baseCopia.loc[i,'auxiliar'] = baseCopia[nombreColumna][i][:7]
        i = i + 1

    baseCopia = baseCopia[(baseCopia['auxiliar'] == fechaCorte)]
    baseCopia = baseCopia.drop(["auxiliar"], axis = 1)

    return baseCopia

def CreditosActivos(carteraActivaActual, carteraActivaAnterior):

    carteraActivaActualCopia = carteraActivaActual.copy()
    carteraActivaAnteriorCopia = carteraActivaAnterior.copy()

    creditoActivaAnterior = carteraActivaAnteriorCopia[['Credito']]
    creditoActivaActual = carteraActivaActualCopia[['Credito','Estado']]

    cruceCreditos = creditoActivaAnterior.merge(creditoActivaActual, how="left", on=["Credito"])

    cruceCreditos = cruceCreditos[(cruceCreditos['Estado'] != "ACTIVO")]

    cruceCreditos = cruceCreditos[['Credito']]
    cruceCreditos = cruceCreditos.merge(carteraActivaAnteriorCopia, how="inner", on=["Credito"])

    carteraActivaActualCopia = pd.concat([carteraActivaActualCopia,cruceCreditos], sort = False)

    return carteraActivaActualCopia

def FechasOriginacion(originacion, carteraActivaActual):

    originacionCopia = originacion.copy()
    carteraActivaActualCopia = carteraActivaActual.copy()

    originacionCopia = originacionCopia[['Credito','Fecha Desembolso','Primera Cuota']]
    carteraActivaActualCopia = carteraActivaActualCopia.merge(originacionCopia, how="left", on=["Credito"])

    return carteraActivaActualCopia

def LlenarUniversalDatosBasicos(universal, carteraActivaActual):

    universalCopia = universal.copy()
    carteraActivaActualCopia = carteraActivaActual.copy()

    universalCopia['CREDITO'] = carteraActivaActualCopia['Credito']
    universalCopia['PRODUCTO'] = carteraActivaActualCopia['Producto']
    universalCopia['DOCUMENTO'] = carteraActivaActualCopia['ID']
    universalCopia['CLIENTE'] = carteraActivaActualCopia['Nombre']
    universalCopia['FECHA_ORIGINACION'] = carteraActivaActualCopia['Fecha Desembolso']
    universalCopia['FECHA PRIMER PAGO'] = carteraActivaActualCopia['Primera Cuota']
    universalCopia['PLAZO'] = carteraActivaActualCopia['Plazo']
    universalCopia = universalCopia.reset_index(drop = True)

    return universalCopia

def RestaCampos(universal, campoUno, camposDos, campoResultado):

    universalCopia = universal.copy()

    i = 1
    while i < len(universalCopia):
        universalCopia.loc[i, campoResultado] = universalCopia[campoUno][i] - universalCopia[camposDos][i]
        i = i + 1

    return universalCopia

def CarteraTipoEstado(base, nombreColumna, estado):

    baseCopia = base.copy()
    
    i = 0
    while i < len (baseCopia):
        baseCopia.loc[i, nombreColumna] = baseCopia[nombreColumna][i].strip()
        i = i + 1
    baseCopia = baseCopia[(baseCopia[nombreColumna] == estado)]

    return baseCopia

def SaldosCapitales(universal, carteraActivaActual, carteraActivaAnterior):

    universalCopia = universal.copy()
    carteraActivaActualCopia = carteraActivaActual.copy()
    carteraActivaAnteriorCopia = carteraActivaAnterior.copy()

    mesActivaAnterior = carteraActivaAnteriorCopia['Fecha de Corte'][0][3:-5]
    mesActivaActual = carteraActivaActualCopia['Fecha de Corte'][0][5:-3]

    carteraActivaAnteriorCopia = carteraActivaAnteriorCopia[['Credito','Saldo Capital']]
    carteraActivaActualCopia = carteraActivaActualCopia[['Credito','Saldo Capital']]

    universalCopia = universalCopia.merge(carteraActivaAnteriorCopia, left_on='CREDITO', right_on='Credito',how="left")
    universalCopia['K INICIAL'] = universalCopia['Saldo Capital']
    universalCopia = LlenarCampoCero(universalCopia, "K INICIAL", 0)
    universalCopia = universalCopia.drop(["Saldo Capital"], axis = 1) 

    universalCopia = universalCopia.merge(carteraActivaActualCopia, left_on='CREDITO', right_on='Credito',how="left")
    universalCopia['K FINAL'] = universalCopia['Saldo Capital']
    universalCopia = LlenarCampoCero(universalCopia, "K FINAL", 0)
    universalCopia = universalCopia.drop(["Saldo Capital"], axis = 1)
    universalCopia = RestaCampos(universalCopia, "K FINAL", "K INICIAL", "MOVIMIENTO CAPITAL")

    universalCopia = RenombrarColumnas(universalCopia,"K INICIAL",mesActivaAnterior) 
    universalCopia = RenombrarColumnas(universalCopia,"K FINAL",mesActivaActual) 

    universalCopia = universalCopia.drop(["Credito_x","Credito_y"], axis = 1)

    return universalCopia

def CausacionCuotas(universal, causacionCuotas):
    
    universalCopia = universal.copy()
    causacionCuotasCopia = causacionCuotas.copy()

    causacionCuotasCopia = causacionCuotasCopia[['CREDITO','FECHA_CUOTA_CAUSADA','INTERESES_CORRIENTES','SEGURO',
    'PERIODO_GRACIA','GAC','IVAGAC','INTERES_MORA','GPS','BUSURA']]

    universalCopia['CREDITO'] = universalCopia['CREDITO'].astype(str)
    causacionCuotasCopia['CREDITO'] = causacionCuotasCopia['CREDITO'].astype(str)
    universalCopia = universalCopia.merge(causacionCuotasCopia, how="left", on=["CREDITO"])

    universalCopia['FECHA_CUOTA_CAUSADA_x'] = universalCopia['FECHA_CUOTA_CAUSADA_y']
    universalCopia['INTERESES_CORRIENTES_x'] = universalCopia['INTERESES_CORRIENTES_y']
    universalCopia['SEGURO_x'] = universalCopia['SEGURO_y']
    universalCopia['PERIODO_GRACIA_x'] = universalCopia['PERIODO_GRACIA_y']
    universalCopia['GAC_x'] = universalCopia['GAC_y']
    universalCopia['IVAGAC_x'] = universalCopia['IVAGAC_y']
    universalCopia['INTERES_MORA_x'] = universalCopia['INTERES_MORA_y'] 
    universalCopia['GPS_x'] = universalCopia['GPS_y']
    universalCopia['BUSURA_x'] = universalCopia['BUSURA_y']

    universalCopia = universalCopia.drop(['FECHA_CUOTA_CAUSADA_y','INTERESES_CORRIENTES_y','SEGURO_y',
    'PERIODO_GRACIA_y','GAC_y','IVAGAC_y','INTERES_MORA_y','GPS_y','BUSURA_y'], axis = 1)

    universalCopia = universalCopia.rename(columns={'FECHA_CUOTA_CAUSADA_x':'FECHA_CUOTA_CAUSADA','INTERESES_CORRIENTES_x':'INTERESES_CORRIENTES'
    ,'SEGURO_x':'SEGURO', 'PERIODO_GRACIA_x':'PERIODO_GRACIA','GAC_x':'GAC','IVAGAC_x':'IVAGAC','INTERES_MORA_x':'INTERES_MORA','GPS_x':'GPS'
    ,'BUSURA_x':'BUSURA'})

    universalCopia = LlenarCampoCero(universalCopia,"INTERESES_CORRIENTES",0)
    universalCopia = LlenarCampoCero(universalCopia,"SEGURO",0)
    universalCopia = LlenarCampoCero(universalCopia,"PERIODO_GRACIA",0)
    universalCopia = LlenarCampoCero(universalCopia,"GAC",0)
    universalCopia = LlenarCampoCero(universalCopia,"IVAGAC",0)
    universalCopia = LlenarCampoCero(universalCopia,"INTERES_MORA",0)
    universalCopia = LlenarCampoCero(universalCopia,"GPS",0)
    universalCopia = LlenarCampoCero(universalCopia,"BUSURA",0)

    return universalCopia

def IntAcuerdosCovid(universal, acuerdos, fechaActual):

    universalCopia = universal.copy()
    acuerdosCopia = acuerdos.copy()

    universalCopia['CREDITO'] = universalCopia['CREDITO'].astype(str)
    acuerdosCopia = acuerdosCopia.rename(columns={'NoCREDITO ACUERDO':'CREDITO'})
    acuerdosCopia['CREDITO'] = acuerdosCopia['CREDITO'].astype(str)
    
    i = 0
    while i < len(universalCopia):
        credito =  universalCopia['CREDITO'][i]
        j = 0
        while j < len(acuerdosCopia):
            creditoAcuerdo = acuerdosCopia['CREDITO'][j][0:len(acuerdosCopia['CREDITO'][j])-2]
            if credito == creditoAcuerdo:
                k = 0
                while k < len (acuerdosCopia.columns):
                    columna = str(acuerdosCopia.columns[k])
                    columna = columna[0:len(columna)-9]
                    if fechaActual == columna:
                        universalCopia.loc[i, 'INT ACUERDOS COVID'] = acuerdosCopia[acuerdosCopia.columns[k]][j]
                    k = k + 1
            j = j + 1 
        i = i + 1
    universalCopia = LlenarCampoCero(universalCopia, "INT ACUERDOS COVID", 0)

    return universalCopia

def VerificacionCuotaCorriente(universal):

    universalCopia = universal.copy()

    i = 0
    while i < len(universalCopia):
        if universalCopia['CUOTA FONDEADOR'][i] == 0:
            universalCopia.loc[i,'VERIFICACION CUOTA CTE'] = 0
        else:
            universalCopia.loc[i,'VERIFICACION CUOTA CTE'] = universalCopia['VALOR CUOTA CREDITO CLIENTE (KIS)-CTA CORRIENTE'][i] - universalCopia['CUOTA FONDEADOR'][i] - universalCopia['PRIMA DELTA'][i]    
        i = i + 1

    return universalCopia

def VerificacionTipoCausacion(universal):

    universalCopia = universal.copy()

    i = 0
    while i < len(universalCopia):
        if universalCopia['FONDEADOR CAUSACION'][i] == "DELTA CREDIT S.A.S.":
            universalCopia.loc[i, 'TIPO DE CAUSACION'] = 1
        else:
            universalCopia.loc[i, 'TIPO DE CAUSACION'] = 3
        i = i + 1

    return universalCopia    

def InformacionCuotaCuota(universal, cuota):

    universalCopia = universal.copy()
    cuotaCopia = cuota.copy()
    
    universalAux = universalCopia[['PRIMA DELTA','CUOTA FONDEADOR','PRIMA FONDEADOR','VALOR CUOTA CREDITO CLIENTE (KIS)-CTA CORRIENTE',
    'CAPITAL DE LA CUOTA','FONDEADOR CAUSACION']]

    i = 0
    while i < len(cuotaCopia.columns):
        cuotaCopia = cuotaCopia.rename(columns={cuotaCopia.columns[i]: cuotaCopia.columns[i]+"_y"})
        i = i + 1

    cuotaCopia = cuotaCopia.rename(columns={"FONDEADOR_y": "FONDEADOR CAUSACION_y"})
    cuotaCopia['NUMERO DE CREDITO_y'] = cuotaCopia['NUMERO DE CREDITO_y'].astype(str)

    universalCopia = universalCopia.merge(cuotaCopia, left_on = 'CREDITO', right_on = 'NUMERO DE CREDITO_y' ,how='left')

    i = 0
    while i < len(universalCopia):
        j = 0
        while j < len(universalAux.columns):
            universalCopia.loc[i, universalAux.columns[j]] = universalCopia[universalAux.columns[j]+"_y"][i]
            j = j + 1
        i = i + 1

    auxColumnas = universalCopia
    i = 0
    while i < len(auxColumnas.columns):
        if auxColumnas.columns[i][-2:] == "_y":
            universalCopia = universalCopia.drop([auxColumnas.columns[i]],axis = 1)
        i = i + 1

    i = 0
    while i < len(universalAux.columns):
        if universalAux.columns[i] != "FONDEADOR CAUSACION":
            universalCopia = LlenarCampoCero(universalCopia,universalAux.columns[i],0)
        else:
            universalCopia = LlenarCampoCero(universalCopia,universalAux.columns[i],"DELTA CREDIT S.A.S.")     
        i = i + 1
    universalCopia = VerificacionCuotaCorriente(universalCopia)
    universalCopia = VerificacionTipoCausacion(universalCopia)

    return universalCopia

def InteresCorrienteAcuerdos(universal):

    universalCopia = universal.copy()

    i = 0
    while i < len(universalCopia):
        if universalCopia['INT ACUERDOS COVID'][i] != 0:
            universalCopia.loc[i,'INTERESES_CORRIENTES'] = universalCopia['INT ACUERDOS COVID'][i]
        i = i + 1

    return universalCopia

def IngresosContabilizar(universal):

    universalCopia = universal.copy()

    universalCopia = universalCopia.rename(columns={'CXCPGRACIA.1':'GPS.1'})    
    valores = universalCopia[['SEGURO','PERIODO_GRACIA','BUSURA','INTERES_MORA','GAC','IVAGAC','INTERESES_CORRIENTES','GPS','PRIMA DELTA']]
    columnas = universalCopia[['SEGURO.2','PERIODO_GRACIA.1','BUSURA.1','MORA.1','GASTOS_DE_COBRANZA.1','IVAGAC.2','INTERESES_CORRIENTES.1','GPS.1','PRIMA DELTA.1']]
    i = 0
    while i < len(universalCopia):
        j = 0
        while j < len(valores.columns):
            if (universalCopia['TIPO DE CAUSACION'][i] == 1) & (columnas.columns[j] == "INTERESES_CORRIENTES.1"):
                universalCopia.loc[i, columnas.columns[j]] = universalCopia[valores.columns[j]][i]
            else:
                universalCopia.loc[i, columnas.columns[j]] = 0   
                if columnas.columns[j] == "PRIMA DELTA.1":
                    universalCopia.loc[i, columnas.columns[j]] = universalCopia[valores.columns[j]][i]

            if columnas.columns[j] != "INTERESES_CORRIENTES.1":
                universalCopia.loc[i, columnas.columns[j]] = universalCopia[valores.columns[j]][i]     
            j = j + 1
        universalCopia.loc[i,'I_INICALES.1'] = 0    
        i = i + 1

    
    return universalCopia

def EspaciosBlanco(universal,campos):

    universalCopia = universal.copy()

    i = 0
    while i < len(universalCopia):
        j = 0
        while j < len(campos):
            universalCopia.loc[i, campos[j]] = universalCopia[campos[j]][i].strip()
            j += 1
        i += 1

    return universalCopia

cursor = ConexionBDSqlServer().cursor()

causacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/FormatoCausacion.xlsx")
universal = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/UNIVERSAL DE MOVIMIENTOS.xlsx")
cuota = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/CUOTA A CUOTA.xlsx")

carteraActual = LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Mensual/CarteraM.csv","|")
carteraAnterior = LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Historico/CarteraH.csv","|")
originacion = LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Historico/OriginacionH.csv","|")

acuerdos = LeerExcelConHoja("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/Acuerdos Contabilidad Causacion mensual.xlsx","Base")

Create("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/CausacionCuotas.sql",cursor)
causacionCuotas = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/CausacionCuotasSELECT.sql")
DeleteSinRuta("DROP TABLE CuotasCausacion", cursor)

fechaCorte = ObtenerFechaCorteAnterior()
fechaActual = ObtenerFechaActual()

carteraAnterior = ObtenerCarteraPorFecha(carteraAnterior, "Fecha de Corte", fechaCorte)

##Cartera Activa
carteraActivaActual = CarteraTipoEstado(carteraActual, "Estado", "ACTIVO")
carteraActivaAnterior = CarteraTipoEstado(carteraAnterior, "Estado", "ACTIVO")

##CarteraConcatenada con fechasOriginacion
carteraActivaActualAnterior = CreditosActivos(carteraActivaActual, carteraActivaAnterior)
carteraActivaActualAnterior = FechasOriginacion(originacion, carteraActivaActualAnterior)

universal = LlenarUniversalDatosBasicos(universal, carteraActivaActualAnterior)

universal = SaldosCapitales(universal, carteraActivaActual, carteraActivaAnterior)

universal = CausacionCuotas(universal, causacionCuotas)

universal = IntAcuerdosCovid(universal, acuerdos, fechaActual)

universal = InformacionCuotaCuota(universal, cuota)

universal = InteresCorrienteAcuerdos(universal)

universal = IngresosContabilizar(universal)

campos = ['FONDEADOR CAUSACION']
universal = EspaciosBlanco(universal,campos)

CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/UniversalDeMovimientos.xlsx", "universal", universal, False)