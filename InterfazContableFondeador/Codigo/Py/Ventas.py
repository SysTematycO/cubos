from LeerConsultas import *
from CRUD import *
from GeneracionSalidas import *
from datetime import datetime
import numpy as np

def ListaMesesLetra():
    meses = pd.DataFrame()
    numeroMes = ['01', '02', '03', '04', '05', '06','07', '08', '09', '10', '11', '12']
    letraMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    meses['Numero Mes'] = numeroMes
    meses['Letra Mes'] = letraMes
    return meses

def MesReporte(base, fecha):

    #fecha = datetime.today()
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    anioMes = fecha.strftime('%Y-%m')

    i = 0
    while i < len(base):
        base['FECHA_VENTA'][i] = base['FECHA_VENTA'][i][:7]
        i += 1 

    base = base[(base['FECHA_VENTA']==anioMes)]
    
    base = base.reset_index(drop = True)

    return base 

def CuentasContables(fondeador, cuentas):
    cuenta = ""
    i = 0
    while i < len(cuentas):
        if cuentas['Concepto '][i] == fondeador:
            cuenta = cuentas['cuenta contable'][i]
        i += 1
    return cuenta

def AsignacionValores(opFondeador, campos, cuentas):
    i = 0
    while i < len(opFondeador):
        match i:
            case 0:
                opFondeador[campos[i]][i] = opFondeador['VR_VENTA'][i]
                #opFondeador[campos[i]][i] = opFondeador['SALDO_CAPITAL_FONDEADOR'][i] + opFondeador['AJUSTE'][i]
                opFondeador['Cuenta Contable'][i] = CuentasContables(opFondeador['FONDEADOR'][i], cuentas)
            case 1:
                opFondeador[campos[i]][i] = opFondeador['SALDO_CAPITAL_FONDEADOR'][i]
                opFondeador['Cuenta Contable'][i] = CuentasContables("CAPITAL", cuentas)
            case 2:
                if opFondeador['AJUSTE'][i] < 0:
                    opFondeador[campos[i]][i] = opFondeador['AJUSTE'][i] * -1
                    opFondeador['Cuenta Contable'][i] = CuentasContables("COSTO DE VENTA", cuentas)
                else:
                    opFondeador[campos[i]][i] = opFondeador['AJUSTE'][i]
                    opFondeador['Cuenta Contable'][i] = CuentasContables("INTERESES", cuentas)                 
        i += 1

    return opFondeador 

def ValoresVenta(cuentas, opFondeador):
    print (opFondeador)
    repeticion = 3
    opFondeador = opFondeador.loc[np.repeat(opFondeador.index.values,repeticion)]
    opFondeador = np.array_split(opFondeador, len (opFondeador) / repeticion)

    i = 0
    while i < len(opFondeador):
        j = 0
        opFondeador[i] = opFondeador[i].reset_index(drop = True)
        opFondeador[i]['Debito'] = 0
        opFondeador[i]['Credito'] = 0
        opFondeador[i]['Cuenta Contable'] = ""
        while j < len(opFondeador[i]):
            if opFondeador[i]['DIFERENCIA_DIAS'][j] <= 30:
                campos = ['Debito','Credito','Credito']
                opFondeador[i] = AsignacionValores(opFondeador[i], campos, cuentas)     
            else:
                campos = ['Debito','Credito','Debito']
                opFondeador[i] = AsignacionValores(opFondeador[i], campos, cuentas)
            j += 1
        i += 1

    i = 0
    while i < len (opFondeador):
        if i == 0:
            base = opFondeador[i]
        if i > 0:    
            base = pd.concat([opFondeador[i],base], sort = False)
        i += 1

    base = base.reset_index(drop = True)
    base['Debito'] = base['Debito'].astype(int)
    base['Credito'] = base['Credito'].astype(int)

    return base

def Formato(formatoVentas, opFondeador, encabezado, datosFormato):

    formatoVentas['Débito'] = opFondeador['Debito']
    formatoVentas['Crédito'] = opFondeador['Credito']
    formatoVentas['Código cuenta contable'] = opFondeador['Cuenta Contable']
    formatoVentas['Identificación tercero'] = opFondeador['CEDULA']

    i = 0
    while i < len(encabezado):
        formatoVentas[encabezado[i]] = datosFormato[i]
        i += 1

    formatoVentas['Observaciones'] = "Venta Cartera " + formatoVentas['Fecha de elaboración ']
    formatoVentas['Descripción'] = "Venta Cartera " + opFondeador['NoCREDITO']
    formatoVentas['Tipo de comprobante'] = "120"
    return formatoVentas

def GenerarExcel(consecutivo, fecha):

    meses = ListaMesesLetra()

    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    anio = fecha.strftime('%Y')
    mes = fecha.strftime('%m')
    
    i = 0
    while i < len(meses):
        if meses['Numero Mes'][i] == mes:
            mes = meses['Letra Mes'][i]
        i += 1

    CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContableFondeador/Salidas/CC 120-"+ consecutivo +" Venta de Cartera "+ mes + " " + anio + ".xlsx","Cargue",formatoVentas,False)
    
cursor = ConexionBDSqlServer()

formatoVentas = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContableFondeador/Codigo/Entradas/FormatoVenta.xlsx")
cuentas = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContableFondeador/Codigo/Entradas/CuentasContables.xlsx")

QueryRuta("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContableFondeador/Codigo/ConsultasSQL/OperacionesFondeadores.sql",cursor)
opFondeador = ReadSinRuta("SELECT * FROM OperacionesFondeadores ORDER BY FECHA_CORTE, NoCREDITO DESC")
QuerySinRuta("DROP TABLE OperacionesFondeadores",cursor)

print ("Fecha Reporte: dd/mm/yyyy")
fecha = input()
print ("Consecutivo")
consecutivo = input()

opFondeador = MesReporte(opFondeador, fecha) 
opFondeador = ValoresVenta(cuentas, opFondeador)

encabezado = ['Fecha de elaboración ','Consecutivo comprobante']
datosFormato = [fecha,consecutivo]
formatoVentas = Formato(formatoVentas, opFondeador, encabezado, datosFormato)

GenerarExcel(consecutivo, fecha)