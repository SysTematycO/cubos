from cmath import isnan
from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from datetime import datetime

import dateutil
import pandas as pd
import numpy as np

def EntradasAplicacionPagos(cursor):
    with open("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/AplicacionPagos.sql") as file_object:
        query = file_object.read() 
        cursor.execute(query)
        cursor.commit()

    with open("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/AplicacionPagosSELECT.sql") as file_object:
        query = file_object.read() 
        datos = ConsultaSQL(query)
        cursor.execute("DROP TABLE AplicacionPagos")
        cursor.commit() 

    return datos

def CuentasContablesSigo():
    rutaCuentas = "C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Tabla cuentas contables Pagos Siigo.xlsx"
    cuentas = pd.read_excel(rutaCuentas)

    return cuentas

def FormatoAplicacionPagos():
    rutaFomato = "C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Formato interfaz contable (Encabezado).xlsx"
    formato = pd.read_excel(rutaFomato)

    return formato

def ActualizarPartida(base,conceptoPrimario,concepto,partida,valor,indicador):

    base.loc[base[conceptoPrimario] == concepto, partida] = base[valor][indicador]

def LlenarFormatoAplicacionPagos(aplicacionPagos,cuentasContablesSigo,formatoAplicacionPagos,meses, cursor):
    
    #Si se agrega una nueva cuenta aumentar en +1 la variable contador pagos
    contadorPagos = len(cuentasContablesSigo)

    aplicacionPagos = aplicacionPagos.loc[np.repeat(aplicacionPagos.index.values,contadorPagos)]

    aplicacionPagos = np.array_split(aplicacionPagos, len (aplicacionPagos) / contadorPagos)

    i = 0
    while i < len (aplicacionPagos):
        aplicacionPagos[i] = aplicacionPagos[i].reset_index(drop=True)
        aplicacionPagos[i] = pd.concat([aplicacionPagos[i], cuentasContablesSigo], axis=1)
        i += 1  

    i = 0
    while i < len (aplicacionPagos):
        if i == 0:
            basePagos = aplicacionPagos[i]
        if i > 0:    
            basePagos = pd.concat([aplicacionPagos[i],basePagos])
        i += 1

    basePagos = basePagos.reset_index(drop=True)

    basePagos = basePagos.drop(basePagos[(basePagos['CUENTA_RECAUDO']!=basePagos['Concepto']) & (basePagos['naturaleza'] == "DEBITO")].index)

    basePagos=basePagos.assign(Débito=0)
    basePagos=basePagos.assign(Crédito=0)
    basePagos=basePagos.assign(RuntIva=(basePagos['RUNT']+basePagos['GARANTIAS_MOBILIARIAS']+basePagos['IVA_GARANTIAS_MOBILIARIAS']))

    basePagos = basePagos.reset_index(drop=True)

    ActualizarPartida(basePagos, "naturaleza", "DEBITO", "Débito", "VALOR_PAGADO",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXC CAPITAL", "Crédito", "KPAGADO",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXC INT CORRIENTE", "Crédito", "IPAGADO",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXC SEGURO", "Crédito", "SEGURO",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "INGRESO INT MORA", "Crédito", "MORA",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "INGRESO GAC", "Crédito", "GASTOS_DE_COBRANZA",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "INGRESO IVA GAC", "Crédito", "IVAGAC",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "SALDO A FAVOR CARTERA PROPIA", "Crédito", "SAFAVOR",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXC RUNT - GM - GM IVA", "Crédito", "RuntIva",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXCPGRACIA", "Crédito", "CXCPGRACIA",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "I_INICALES", "Crédito", "I_INICALES",basePagos.index)
    ActualizarPartida(basePagos, "Concepto", "CXC GPS", "Crédito", "GPS_PAGADO",basePagos.index)

    formatoAplicacionPagos['Código cuenta contable'] = basePagos['cuenta contable']
    formatoAplicacionPagos['Identificación tercero'] = basePagos['DOCUMENTO']

    i = 0
    while i < len (basePagos['FECHA_PAGO']):
        fechaAplicacion = basePagos['FECHA_PAGO'][i]
        fechaAplicacion = dateutil.parser.parse(fechaAplicacion)
        fechaAplicacion = fechaAplicacion.strftime('%d/%m/%Y')
        basePagos['FECHA_PAGO'][i] = fechaAplicacion
        i += 1

    formatoAplicacionPagos['Descripción'] = 'APLICACIÓN PAGOS ' +  basePagos['CREDITO'] + " " + basePagos['FECHA_PAGO']

    formatoAplicacionPagos['Débito'] = basePagos['Débito']

    formatoAplicacionPagos['Crédito'] = basePagos['Crédito']    

    i = 0
    while i < len(basePagos['FECHA_PAGO']):
        basePagos['FECHA_PAGO'][i] = str(basePagos['FECHA_PAGO'][i][-4:]) + '-' + str(basePagos['FECHA_PAGO'][i][3:-5]) + '-' + str(basePagos['FECHA_PAGO'][i][:2])
        i += 1
    
    basePagos['MES'] = pd.DatetimeIndex(basePagos['FECHA_PAGO']).month
    basePagos = basePagos.merge(meses, left_on='MES', right_on='MesNum')

    formatoAplicacionPagos['Observaciones'] = "APLICACIÓN " + basePagos['MesLetra']
    formatoAplicacionPagos['Tipo de comprobante'] = "110"

    print ("Ultima Fecha")    
    fecha = input()    
    formatoAplicacionPagos['Fecha de elaboración '] = fecha

    formatoAplicacionPagos = formatoAplicacionPagos.drop(formatoAplicacionPagos[(formatoAplicacionPagos['Débito']==0) & (formatoAplicacionPagos['Crédito']==0)].index)
    formatoAplicacionPagos = formatoAplicacionPagos.drop(formatoAplicacionPagos[(formatoAplicacionPagos['Crédito']<0)].index)

    formatoAplicacionPagos = formatoAplicacionPagos.reset_index(drop=True)
    formatoAplicacion = np.array_split(formatoAplicacionPagos, len(formatoAplicacionPagos))

    i = 0
    totalRegistros = 0


    print ("Consecutivo")    
    consecutivoPagos = input()  
    
    concatenarCredito = formatoAplicacion[i]
    auxiliar = formatoAplicacion[i]

    concatenarCredito = concatenarCredito.drop(concatenarCredito.index)
    auxiliar = auxiliar.drop(auxiliar.index)

    while i < len (formatoAplicacion):
        if i == 0:
            distribucion = formatoAplicacion[i]
        if i > 0:
            concatenarCredito = pd.concat([concatenarCredito,formatoAplicacion[i]])

            if concatenarCredito['Crédito'][i]==0:
                totalRegistros = len (distribucion) + len (concatenarCredito)
                
                if totalRegistros > 500:

                    auxiliar = distribucion[-1:]
                    distribucion = distribucion.drop(distribucion.index[len(distribucion)-1])

                    consecutivo = str(consecutivoPagos)
                    distribucion['Consecutivo comprobante'] = consecutivo
                    CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/AplicacionPagos/AplicacionPagos "+ consecutivo +".xlsx", "AplicacionPagos", distribucion, False)
                    consecutivoPagos = int(consecutivoPagos) + 1

                    distribucion = distribucion.drop(distribucion.index)

                    distribucion = auxiliar
                    auxiliar = auxiliar.drop(auxiliar.index)
                else:
                    distribucion = pd.concat([distribucion,concatenarCredito])
                    concatenarCredito = concatenarCredito.drop(concatenarCredito.index)  
        i += 1
    
    if len (distribucion) > 0:
        distribucion = pd.concat([distribucion,concatenarCredito])
        consecutivo = str(consecutivoPagos)
        distribucion['Consecutivo comprobante'] = consecutivo
        CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/AplicacionPagos/AplicacionPagos "+ consecutivo +".xlsx", "AplicacionPagos", distribucion, False)
        consecutivoPagos = int(consecutivoPagos) + 1


meses = pd.read_excel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Meses.xlsx")

cursor = ConexionBDSqlServer().cursor()
aplicacionPagos = EntradasAplicacionPagos(cursor)
cuentasContablesSigo = CuentasContablesSigo()
formatoAplicacionPagos = FormatoAplicacionPagos()

LlenarFormatoAplicacionPagos(aplicacionPagos,cuentasContablesSigo,formatoAplicacionPagos,meses,cursor)

        