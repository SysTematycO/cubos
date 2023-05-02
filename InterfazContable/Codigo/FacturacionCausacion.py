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

def RegistrosCausacion(causacion):
    causacion = causacion.groupby(["Identificación tercero", "Código cuenta contable"], as_index = False)["Débito","Crédito"].sum()
    
    causacion['Código cuenta contable'] = causacion['Código cuenta contable'].astype(str)
    causacion['Codigo'] = causacion['Código cuenta contable'].str[0:2]

    causacion = causacion[(causacion['Codigo']=="28")]
    causacion = causacion.reset_index(drop = True)

    causacion = causacion.drop(["Codigo"], axis = 1)

    return causacion

def ConceptosProductos(base, conceptos):
    base['Código cuenta contable'] = base['Código cuenta contable'].astype(str)
    conceptos['Cuenta contable'] = conceptos['Cuenta contable'].astype(str)
    base = base.merge(conceptos, how = 'left', left_on = 'Código cuenta contable', right_on = 'Cuenta contable')
    return base

def CodigoImpuesto(base):

    base['Valor Forma Pago'] = base['Crédito']
    base['Valor unitario'] = 0
    base['Codigo Impuesto Cargo'] = ""

    i = 0
    while i < len(base):
        if (base['Cuenta contable'][i] == '28151003') | (base['Cuenta contable'][i] == '28151008'):
            base.loc[i, 'Valor unitario'] = base['Valor Forma Pago'][i] / 1.19
            base.loc[i, 'Codigo Impuesto Cargo'] = 24
        else:
            base['Valor unitario'][i] = base['Valor Forma Pago'][i]
        i += 1

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

def LlenarFormato(facturacionCausacion, base, consecutivo):

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

    facturacionCausacion['Identificación tercero'] = base['Identificación tercero'].astype(str)

    facturacionCausacion['Tipo de comprobante'] = "1"
    
    base = Consecutivo(base, consecutivo)
    facturacionCausacion['Consecutivo'] = base['Consecutivo']

    facturacionCausacion['Fecha de elaboración  '] = fechaActual
    
    base = NombrePersona(base)
    facturacionCausacion['Nombre contacto'] = base['Nombres']
    facturacionCausacion['Email Contacto'] = "facturacion@deltacredit.com.co"

    facturacionCausacion['Código producto'] = base['Código']
    facturacionCausacion['Descripción producto'] = base['Nombre']
    facturacionCausacion['Identificación vendedor'] = "1014243220"
    facturacionCausacion['Cantidad producto'] = 1
    facturacionCausacion['Valor unitario'] = base['Valor unitario']
    facturacionCausacion['Código impuesto cargo'] = base['Codigo Impuesto Cargo']
    facturacionCausacion['Código forma de pago'] = base['Medio de Pago']
    facturacionCausacion['Valor Forma de Pago'] = base['Valor Forma Pago']
    facturacionCausacion['Fecha Vencimiento'] = fechaVencimiento 
    facturacionCausacion['Observaciones'] = ""
    facturacionCausacion = Observaciones(facturacionCausacion)
    return facturacionCausacion

causacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Causacion/Causacion.xlsx")
facturacionCausacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/FacturacionCausacion/FormatoCausacion.xlsx")
conceptos = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/FacturacionCausacion/Conceptos Facturacion Electronica V 20220426.xlsx")

base = RegistrosCausacion(causacion)

base = ConceptosProductos(base, conceptos)

base = CodigoImpuesto(base)

print("Consecutivo")
consecutivo = input()
facturacionCausacion = LlenarFormato(facturacionCausacion, base, int(consecutivo))

CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/FacturacionCausacion/FacturacionCausacion.xlsx","base",facturacionCausacion,False)