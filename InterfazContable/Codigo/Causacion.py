from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from datetime import datetime
from CRUD import *
import numpy as np 

def CarteraPropia(cuentas, universal, cantidad):

    universalCopia = universal.copy()
    cuentasCopia = cuentas.copy()

    vendida = False
    try:
        cuentasFondeador = cuentasCopia[['FONDEADOR','cta contable']]
        cuentasFondeador = cuentasFondeador.dropna()
        vendida = True
    except:
        vendida = False

    cuentasCopia = cuentasCopia[['Concepto ','cuenta contable','Tercero ','Nombre cuenta Contable','naturaleza']]
    cuentasCopia = cuentasCopia.dropna()

    universalCopia = universalCopia.loc[np.repeat(universalCopia.index.values,cantidad)]

    universalCopia = np.array_split(universalCopia, len (universalCopia) / cantidad)

    i = 0
    while i < len (universalCopia):
        universalCopia[i] = universalCopia[i].reset_index(drop=True)
        universalCopia[i] = pd.concat([universalCopia[i], cuentasCopia], axis = 1)
        i += 1

    i = 0
    while i < len(universalCopia):
        j = 0
        universalCopia[i]['Débito'] = 0
        universalCopia[i]['Crédito'] = 0
        while j < len(universalCopia[i]):
            if (universalCopia[i]['Concepto '][j] == "CXP OTROS FONDEADR"):
                universalCopia[i].loc[j, 'Concepto '] = "CUOTA FONDEADOR"
            if (universalCopia[i]['Tercero '][j] == 'DEBITO '):
                universalCopia[i].loc[j, 'Débito'] = universalCopia[i][universalCopia[i]['Concepto '][j]][j]
            elif (universalCopia[i]['Tercero '][j] == 'CREDITO '):
                universalCopia[i].loc[j, 'Crédito'] = universalCopia[i][universalCopia[i]['Concepto '][j]][j]
            j += 1
        i += 1

    i = 0
    while i < len(universalCopia):
        if i > 0:
            universalCopia[0] = pd.concat([universalCopia[0],universalCopia[i]], axis = 0)
        i += 1

    universalCopia[0] = universalCopia[0].reset_index(drop=True)        
    universalCopia[0] = universalCopia[0].drop(universalCopia[0][(universalCopia[0]['Débito']==0) & (universalCopia[0]['Crédito'] == 0)].index)
    universalCopia[0] = universalCopia[0].reset_index(drop=True)

    if vendida == True:
        i = 0
        while i < len(universalCopia[0]):
            if universalCopia[0]['Concepto '][i] == "CUOTA FONDEADOR":
                universalCopia[0].loc[i, 'Concepto '] = universalCopia[0]['FONDEADOR CAUSACION'][i]
            i += 1
        universalCopia[0] = universalCopia[0].merge(cuentasFondeador, how = 'left', left_on = 'Concepto ', right_on = 'FONDEADOR')

        i = 0
        while i < len(universalCopia[0]):
            if universalCopia[0]['cuenta contable'][i] == '*':
                universalCopia[0].loc[i, 'cuenta contable'] = universalCopia[0]['cta contable'][i]
            i += 1
        universalCopia[0] = universalCopia[0].drop(['FONDEADOR', 'cta contable','Credito','Cuota Corriente','CAPITAL'], axis = 1)   

    return universalCopia[0]

def Capital(universal,cartera):

    universalCopia = universal.copy()
    carteraCopia = cartera.copy()

    carteraCopia = carteraCopia[['Credito','Cuota Corriente']]
    universalCopia = universalCopia.merge(carteraCopia, how = 'left', left_on = 'CREDITO', right_on = 'Credito')
    universalCopia['CAPITAL'] = universalCopia['Cuota Corriente'] - universalCopia['INTERESES_CORRIENTES']

    return universalCopia

def LlenarFormato(universalP, universalV, causacion):

    universalPCopia = universalP.copy()
    universalVCopia = universalV.copy()
    causacionCopia = causacion.copy()

    universal = pd.concat([universalPCopia,universalVCopia])
    universal['CREDITO'] = universal['CREDITO'].astype(str)
    causacionCopia['Débito'] = universal['Débito']
    causacionCopia['Crédito'] = universal['Crédito']
    causacionCopia['Código cuenta contable'] = universal['cuenta contable']
    causacionCopia['Identificación tercero'] = universal['DOCUMENTO']
    causacionCopia['Descripción'] = 'CAUSACIÓN ' + "" + universal['CREDITO']
    causacionCopia['Tipo de comprobante'] = "105"
    fecha = datetime.today()
    fecha = fecha.strftime('%d/%m/%Y')
    causacionCopia['Fecha de elaboración '] = fecha
    causacionCopia['Observaciones'] = "CAUSACIÓN"

    return causacionCopia

def ListaMesesLetra():
    meses = pd.DataFrame()
    numeroMes = ['01', '02', '03', '04', '05', '06','07', '08', '09', '10', '11', '12']
    letraMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    meses['Numero Mes'] = numeroMes
    meses['Letra Mes'] = letraMes

    fecha = datetime.now()
    mes = fecha.strftime('%m')

    meses =  meses[(meses['Numero Mes'] == mes)]
    
    meses = meses.reset_index(drop = True)

    mes = meses['Letra Mes'][0]

    return mes

def ParticionFormato(causacion, consecutivo):

    causacionCopia = causacion.copy()

    mes = ListaMesesLetra()
    causacionCopia = causacionCopia.reset_index(drop = True)
    causacionCopia = np.array_split(causacionCopia, len(causacionCopia))
    a = []
    p = []

    i = 0
    while i < len(causacionCopia):
        if i > 0:
            if causacionCopia[i]['Descripción'][i] != causacionCopia[i-1]['Descripción'][i-1]:
                totalRegistros = len (p) + len (a)
                if totalRegistros < 500:
                    j = 0
                    while j < len(a):
                        p.append(a[j])
                        j += 1
                    a = []    
                else:
                     k = 0
                     while k < len(p):
                        if k > 0:
                            base = pd.concat([base, causacionCopia[p[k]]])
                        else:
                            base = causacionCopia[p[k]]     
                        k += 1
                     CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Causacion/105 - " + str(consecutivo) + " Causación " + mes + ".xlsx","Cargue_causacion",base,False)
                     consecutivo += 1   
                     p = []    
            a.append(i)    
        else:
            a.append(i)        
            
        i += 1

    i = 0
    while i < len(a):
        p.append(a[i])
        i += 1

    i = 0
    while i < len(p):
        if i > 0:
            base = pd.concat([base, causacionCopia[p[i]]])
        else:
            base = causacionCopia[p[i]]     
        i += 1

    CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Causacion/105 - " + str(consecutivo) + " Causación " + mes + ".xlsx","Cargue_causacion",base,False)

universal = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/UniversalDeMovimientos.xlsx")
cuentas = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/Cuenta cartera propia 1.xlsx")
cuentasVendidas = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/Cuentas Cartera Vendida 3.xlsx")
causacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Causacion/FormatoCausacion.xlsx")
cartera = LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Mensual/CarteraM.csv","|")

universalPropia = universal[(universal['TIPO DE CAUSACION']==1)]
universalPropia = universalPropia.reset_index(drop=True)
universalVendida = universal[(universal['TIPO DE CAUSACION']!=1)]
universalVendida = universalVendida.reset_index(drop=True)

universalPropia = CarteraPropia(cuentas, universalPropia, len(cuentas))

universalVendida = Capital(universalVendida, cartera)
universalVendida = CarteraPropia(cuentasVendidas, universalVendida, len(cuentasVendidas['Concepto ']))

causacion = LlenarFormato(universalPropia, universalVendida, causacion)

print ("Consecutivo:")
consecutivo = input()
consecutivo = int(consecutivo)
CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Causacion/Causacion.xlsx","Cargue_causacion",causacion,False)
causacion = ParticionFormato(causacion, consecutivo)
