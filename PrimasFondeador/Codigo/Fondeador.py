from email.mime import base
from http.client import CONFLICT
from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *

import pandas as pd
import numpy as np

def TraerDatos(ruta):

    with open(ruta) as file_object:
        query = file_object.read() 
        datos = ConsultaSQL(query)

    return datos

def AumentarMes(fecha):
    
    anio = int(fecha[0:4])
    mes = int(fecha[5:7])
    dia = fecha[8:10]

    mes = mes + 1

    if mes>12:
        mes = 1
        anio = anio + 1
    anio = str(anio)    
    mes = str(mes)

    if len(mes) == 1:
        mes = "0" + mes

    fecha = anio + "-" + mes + "-" + dia

    return fecha

def FondeadorCuotas(datos, baseFondeador):

    #Variables cliente
    contadorWhile = 0
    contadorCuotas = 0
    saldoDesembolado = 0
    otrosConceptos = 0
    capital = 0
    interesDeudor = 0
    contadorAuxiliar = 0

    #VariablesFondeador
    saldoDesemboladoVenta = 0
    fechaVentaValidacion = False
    noCuota = 0

    otrosConceptos = ConsultaSQL("SELECT IdPrestamo, Valor FROM prestamoscargos WHERE TipoCargo = 'CUOTA'")

    while contadorWhile < len (datos):  
        print (contadorWhile)
        contadorCuotas = datos['Plazo'][contadorWhile]
        contadorCuotas = contadorAuxiliar + contadorCuotas
        saldoDesembolado = datos['CapitalInicial'][contadorWhile]
        fechaInicial = datos['FechaInicial'][contadorWhile]

        while contadorAuxiliar < contadorCuotas:
            
            fechaInicial = AumentarMes(fechaInicial)
            #anMes = fechaInicial[0:7]

            #Calculamos valores de cara al cliente
            baseFondeador['FECHA_CUOTA'][contadorAuxiliar] = fechaInicial

            numeroCredito = datos['Ctivo'][contadorWhile].astype(str)
            numeroCredito = numeroCredito[:-2]

            baseFondeador['No. CREDITO'][contadorAuxiliar] = numeroCredito

            interesDeudor = saldoDesembolado * datos['Interes'][contadorWhile] / 100

            baseFondeador['INTERES DEUDOR'][contadorAuxiliar] = interesDeudor

            idPrestamo = datos['IdPrestamo'][contadorWhile].astype(str)
            idPrestamo = idPrestamo[:-2] 

            contadorConceptos = 0
            sumaOtrosConceptos = 0

            while contadorConceptos < len (otrosConceptos):
                if otrosConceptos['IdPrestamo'][contadorConceptos] == datos['IdPrestamo'][contadorWhile]:
                    sumaOtrosConceptos = sumaOtrosConceptos + otrosConceptos['Valor'][contadorConceptos]
                contadorConceptos = contadorConceptos + 1

            baseFondeador['OTROS CARGOS DEUDOR'][contadorAuxiliar] = sumaOtrosConceptos

            capital = datos['ValorCuotaCorriente'][contadorWhile] - baseFondeador['INTERES DEUDOR'][contadorAuxiliar]

            baseFondeador['CAPITAL DEUDOR'][contadorAuxiliar] = capital

            baseFondeador['FLUJO DEUDOR'][contadorAuxiliar] = datos['ValorCuotaCorriente'][contadorWhile]

            saldoDesembolado = saldoDesembolado - capital

            baseFondeador['SALDO PROYECTADO DEUDOR'][contadorAuxiliar] = saldoDesembolado
            ########################

            #Calculamos valores de cara al fondeador
            if fechaVentaValidacion == True:
                noCuota = noCuota + 1
                baseFondeador['NO. CUOTA FONDEADOR'][contadorAuxiliar] = noCuota
                baseFondeador['CAPITAL FONDEADOR'][contadorAuxiliar] = capital

                interesVenta = saldoDesemboladoVenta * datos['InteresVenta'][contadorWhile] / 100

                baseFondeador['INTERES FONDEADOR'][contadorAuxiliar] = interesVenta
                baseFondeador['FLUJO FONDEADOR'][contadorAuxiliar] = capital + interesVenta
                baseFondeador['OTROS CARGOS FONDEADOR'][contadorAuxiliar] = 0

                saldoDesemboladoVenta = saldoDesemboladoVenta - capital
                baseFondeador['SALDO PROYECTADO FONDEADOR'][contadorAuxiliar] = saldoDesemboladoVenta 
                baseFondeador['SALDO PROYECTADO FONDEADOR'][contadorAuxiliar] = saldoDesemboladoVenta 

            if (contadorAuxiliar+datos['PlazoVenta'][contadorWhile]+1) >= contadorCuotas:
                fechaVentaValidacion = True
                saldoDesemboladoVenta = saldoDesembolado
                baseFondeador['NO. CUOTA FONDEADOR'][contadorAuxiliar] = noCuota
                baseFondeador['SALDO PROYECTADO FONDEADOR'][contadorAuxiliar] = saldoDesemboladoVenta 
            contadorAuxiliar = contadorAuxiliar + 1

        noCuota = 0
        fechaVentaValidacion = False
        contadorWhile = contadorWhile + 1

    return baseFondeador    

datos = TraerDatos("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/PrimasFondeador/Codigo/ConsultasSQL/PrestamosVFCC.sql")
baseFondeador = pd.read_excel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/PrimasFondeador/Codigo/Entradas/Fondeador.xlsx")

baseFondeador = pd.DataFrame(columns=['FECHA_CUOTA','No. CREDITO', 
'FLUJO DEUDOR','CAPITAL DEUDOR','INTERES DEUDOR','OTROS CARGOS DEUDOR','SALDO PROYECTADO DEUDOR',
'NO. CUOTA FONDEADOR','FLUJO FONDEADOR','CAPITAL FONDEADOR','INTERES FONDEADOR','OTROS CARGOS FONDEADOR','SALDO PROYECTADO FONDEADOR'],index=range(100000))

baseFondeador = FondeadorCuotas(datos,baseFondeador)
baseFondeador = baseFondeador[baseFondeador['No. CREDITO'].notna()]

CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/PrimasFondeador/Salidas/base.xlsx","base", baseFondeador, False)
