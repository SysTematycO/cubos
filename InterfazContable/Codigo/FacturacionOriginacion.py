from cmath import isnan
from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from CRUD import *

import datetime
import pandas as pd
import numpy as np

def UltimoDia(any_day): 
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def RegistrosOriginacion(originacion):
    originacion = originacion.groupby(["Identificación tercero", "Código cuenta contable"], as_index = False)[["Débito","Crédito"]].sum()
    
    originacion['Código cuenta contable'] = originacion['Código cuenta contable'].astype(str)
    originacion['Codigo'] = originacion['Código cuenta contable'].str[0:2]

    originacion = originacion[(originacion['Codigo']=="28")]
    originacion = originacion.reset_index(drop = True)

    originacion = originacion.drop(["Codigo"], axis = 1)

    return originacion

def ConceptosProductos(base, conceptos):
    base['Código cuenta contable'] = base['Código cuenta contable'].astype(str)
    conceptos['Cuenta contable'] = conceptos['Cuenta contable'].astype(str)
    base = base.merge(conceptos, how = 'left', left_on = 'Código cuenta contable', right_on = 'Cuenta contable')
    return base

def CodigoImpuesto(base, valorRunt, valorRgm):

    runt = base[(base['Nombre'] == "Garantias - RUNT")]
    cpRunt = base[(base['Nombre'] == "Garantias - RUNT")] 
    base = base[(base['Nombre'] != "Garantias - RUNT")]

    runt['Valor unitario'] = valorRunt
    cpRunt['Valor unitario'] = valorRgm
    base['Valor unitario'] = base['Crédito']

    runt['Codigo Impuesto Cargo'] = ""
    cpRunt['Codigo Impuesto Cargo'] = 24

    runt['Nombre'] = "RUNT"
    cpRunt['Nombre'] = "RGM"

    runt['Valor Forma Pago'] = runt['Valor unitario']
    cpRunt['Valor Forma Pago'] = cpRunt['Valor unitario'] * 1.19
    base['Valor Forma Pago'] = base['Crédito']

    runt = runt.reset_index(drop = True)
    cpRunt = cpRunt.reset_index(drop = True)

    runt = pd.concat([runt,cpRunt], sort = False)
    runt = runt.reset_index(drop = True)

    base = pd.concat([base,runt], sort = False)
    base = base.reset_index(drop = True)
     
    return base    

def NombrePersona(base):

    personas = ReadSinRuta("SELECT DISTINCT NDOC, Nombres FROM personas")
    personas['NDOC'] = personas['NDOC'].astype(str)
    base['Identificación tercero'] = base['Identificación tercero'].astype(str)
    base = base.merge(personas, how = 'left', left_on = 'Identificación tercero', right_on = 'NDOC')
    base = base.drop("NDOC", axis = 1)

    return base

def Consecutivo(base, consecutivo):
    base['Consecutivo'] = 0
    i = 0
    while i < len(base):
        if i!=0:
            if base['Identificación tercero'][i] != base['Identificación tercero'][i-1]:
                consecutivo += 1
        base.loc[i, 'Consecutivo'] = consecutivo
        i += 1

    return base

def Observaciones(base):
    
    i = 0
    while i < len(base):
        if i != 0:
            if base['Identificación tercero'][i] != base['Identificación tercero'][i-1]:
                base.loc[i, 'Observaciones'] = "En caso de alguna inquietud, enviar su solicitud al correo servicioalcliente@deltacredit.com.co, recuerde que los valores informados en el presente documento corresponden a la cuota del periodo de facturación, y su valor a pagar es el indicado en su “Documento para pago”"
        else:
            base.loc[i, 'Observaciones'] = "En caso de alguna inquietud, enviar su solicitud al correo servicioalcliente@deltacredit.com.co, recuerde que los valores informados en el presente documento corresponden a la cuota del periodo de facturación, y su valor a pagar es el indicado en su “Documento para pago”"    
        i += 1

    return base

def LlenarFormato(facturacionOriginacion, base, consecutivo):

    base = base.sort_values(by=['Identificación tercero'], ascending=True)
    base = base.reset_index(drop = True)

    fechaActual = datetime.date.today()
    mesActual = fechaActual.strftime('%m')
    anioActual = fechaActual.strftime('%Y')

    mesActual = int(mesActual)
    anioActual = int(anioActual)
    fechaActual = UltimoDia(datetime.date(anioActual, mesActual, 1))
    fechaActual = fechaActual.strftime('%d/%m/%Y')

    mesSiguiente = mesActual + 1
    if(mesSiguiente>12):
        mesSiguiente = 1
        anioActual += 1
    fechaVencimiento = UltimoDia(datetime.date(anioActual, mesSiguiente, 1))
    fechaVencimiento = fechaVencimiento.strftime('%d/%m/%Y')

    facturacionOriginacion['Identificación tercero'] = base['Identificación tercero'].astype(str)
    facturacionOriginacion['Tipo de comprobante'] = "1"

    base = Consecutivo(base, consecutivo)
    facturacionOriginacion['Consecutivo'] = base['Consecutivo']

    facturacionOriginacion['Fecha de elaboración  '] = fechaActual

    base = NombrePersona(base)
    facturacionOriginacion['Nombre contacto'] = base['Nombres']
    facturacionOriginacion['Email Contacto'] = "facturacion@deltacredit.com.co"

    facturacionOriginacion['Código producto'] = base['Código']
    facturacionOriginacion['Descripción producto'] = base['Nombre']
    facturacionOriginacion['Identificación vendedor'] = "1014243220"
    facturacionOriginacion['Cantidad producto'] = 1
    facturacionOriginacion['Valor unitario'] = base['Valor unitario']
    facturacionOriginacion['Código impuesto cargo'] = base['Codigo Impuesto Cargo']
    facturacionOriginacion['Código forma de pago'] = base['Medio de Pago']
    facturacionOriginacion['Valor Forma de Pago'] = base['Valor Forma Pago']
    facturacionOriginacion['Fecha Vencimiento'] = fechaVencimiento 
    facturacionOriginacion['Observaciones'] = ""
    facturacionOriginacion = Observaciones(facturacionOriginacion)
    
    return facturacionOriginacion

originacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Originacion.xlsx")
facturacionOriginacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/FacturacionOriginacion/FormatoFacturacion.xlsx")
conceptos = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/FacturacionOriginacion/Conceptos Facturacion Electronica V 20220426.xlsx")

base = RegistrosOriginacion(originacion)

base = ConceptosProductos(base, conceptos)

base = CodigoImpuesto(base, 8000, 39000)

print("Consecutivo")
consecutivo = input()
facturacionOriginacion = LlenarFormato(facturacionOriginacion, base, int(consecutivo))

CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/FacturacionOriginacion/FacturacionOriginacion.xlsx","base",facturacionOriginacion,False)