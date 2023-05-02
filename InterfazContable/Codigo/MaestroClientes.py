from calendar import c
from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *

import pandas as pd
import numpy as np


def EliminarTildes(dataFrame,columna):
    letra = ['á','é','í','ó','ú','Á','É','Í','Ó','Ú']
    letraCorregida = ['a','e','i','o','u','A','E','I','O','U']

    i = 0
    while i < len(letra):
        dataFrame[columna] = dataFrame[columna].str.replace(letra[i],letraCorregida[i])
        i += 1

def EliminarSimbolos(dataFrame,columna):

    letras = ['#', '-', '*', '.', ',', ';', '|', '/', '%', '_', ':']
    for letra in letras:
        dataFrame[columna] = dataFrame[columna].str.replace(letra,'')

def EliminarEspaciosSobrantes(dataFrame,columna):

    datos = dataFrame[columna].str.strip()

    cadenaGuardada = ""
    quitarEspacio = True
    caracterAnterior = False 

    contadorWhile = 0
    contadorWhileDireccion = 0

    while contadorWhile < len (datos):
        direccion = datos[contadorWhile]

        while contadorWhileDireccion < len (direccion):
            if direccion[contadorWhileDireccion] == " ":
                if direccion[contadorWhileDireccion+1] == " ":
                    quitarEspacio = False
            if direccion[contadorWhileDireccion-1] != " ":
                caracterAnterior = True
            if quitarEspacio == True | caracterAnterior == True:
                cadenaGuardada += direccion[contadorWhileDireccion]

            quitarEspacio = True
            caracterAnterior = False    
            contadorWhileDireccion += 1
            
        dataFrame[columna][contadorWhile] = cadenaGuardada
        cadenaGuardada = ""    
        contadorWhileDireccion = 0
        contadorWhile += 1

    return dataFrame[columna]
   

def CruceOriginacionMaestro(baseOriginacion, maestroClientes):
    baseOriginacion['ID_NoCredito'] = baseOriginacion['Identificación tercero'] + baseOriginacion['NoCredito']
    maestroClientes['ID_NoCredito'] = maestroClientes['NDOCUMENTO_TITULAR'] + maestroClientes['CREDITO']
    baseOriginacion = baseOriginacion.drop_duplicates(subset = "ID_NoCredito")

    maestroClientes = maestroClientes.merge(baseOriginacion, left_on='ID_NoCredito', right_on='ID_NoCredito')
    
    with open("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/HomologacionTDOC.sql") as file_object:
        query = file_object.read() 
        homologacion = ConsultaSQL(query)

    homologacion['Nivel'] = homologacion['Nivel'].apply(lambda x: str(x))

    maestroClientes = maestroClientes.merge(homologacion, left_on='TDOCUMENTO_TITULAR', right_on='Nivel')    
    return maestroClientes


def LlenarFormatoMaestroClientes(maestroClientes):

    formato = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Subir Terceros desde Excel - Siigo Nube_CO_preliminar - Formato.xlsm")
    homologacionTiposDoc = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/HomologacionTipoDoc.xlsx")
    codigosDepartamento = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Países-Departamentos-Ciudades.xlsx")

    maestroClientes = maestroClientes.merge(homologacionTiposDoc, left_on='Descripcion', right_on='TipoDoc')
    maestroClientes['TDOCUMENTO_TITULAR'] = maestroClientes['NivelTipoDoc']

    formato['Identificación (Obligatorio)'] = maestroClientes['NDOCUMENTO_TITULAR']
    formato['Tipo identificación'] = maestroClientes['NivelTipoDoc']

    formato['Tipo (Obligatorio)']= np.where((formato['Tipo identificación'] != 31)&(formato['Tipo identificación'] != 50), 'Es persona', 'Es empresa')

    formato['Nombres del tercero (Obligatorio)'] = maestroClientes['NOMBRES_TITULAR']
    formato['Apellidos del tercero (Obligatorio)'] = maestroClientes['APELLIDOS_TITULAR']

    EliminarSimbolos(maestroClientes, "DIRECCION_TITULAR")
    maestroClientes['DIRECCION_TITULAR'] = EliminarEspaciosSobrantes(maestroClientes, "DIRECCION_TITULAR")
    formato['Dirección'] = maestroClientes['DIRECCION_TITULAR']

    EliminarTildes(codigosDepartamento,"Estado / Departamento")
    EliminarTildes(codigosDepartamento,"Ciudad")

    EliminarTildes(maestroClientes,"CIUDAD_TITULAR")
    EliminarTildes(maestroClientes,"DEPARTAMENTO_TITULAR")
    
    codigosDepartamento['Estado / Departamento'] = codigosDepartamento['Estado / Departamento'].str.upper()
    codigosDepartamento['Ciudad'] = codigosDepartamento['Ciudad'].str.upper()
    maestroClientes['CIUDAD_TITULAR'] = maestroClientes['CIUDAD_TITULAR'].str.upper()
    maestroClientes['DEPARTAMENTO_TITULAR'] = maestroClientes['DEPARTAMENTO_TITULAR'].str.upper()

    codigosDepartamento['Estado / Departamento'] = codigosDepartamento['Estado / Departamento'].str.strip()
    codigosDepartamento['Ciudad'] = codigosDepartamento['Ciudad'].str.strip()
    maestroClientes['CIUDAD_TITULAR'] = maestroClientes['CIUDAD_TITULAR'].str.strip()
    maestroClientes['DEPARTAMENTO_TITULAR'] = maestroClientes['DEPARTAMENTO_TITULAR'].str.strip()

    codigosDepartamento['Estado / Departamento'] = codigosDepartamento['Estado / Departamento'].replace(['BOGOTA D.C'], 'BOGOTA D.C.')
    codigosDepartamento['Ciudad'] = codigosDepartamento['Ciudad'].replace(['BOGOTA D.C'], 'BOGOTA D.C.')
    codigosDepartamento['Estado / Departamento'] = codigosDepartamento['Estado / Departamento'].replace(['BOGOTA D.C.'], 'CUNDINAMARCA')

    codigosDepartamento['DepartamentoCiudad'] = codigosDepartamento['Estado / Departamento'] + " " + codigosDepartamento['Ciudad']
    maestroClientes['DepartamentoCiudad'] = maestroClientes['DEPARTAMENTO_TITULAR'] + " " + maestroClientes['CIUDAD_TITULAR']

    maestroClientes = maestroClientes.merge(codigosDepartamento, left_on='DepartamentoCiudad', right_on='DepartamentoCiudad')

    formato['Código pais'] = maestroClientes['Código país']

    i = 0
    maestroClientes['Código Estado / Departamento'] = maestroClientes['Código Estado / Departamento'].astype(str)
    while i < len(maestroClientes['Código Estado / Departamento']):
        maestroClientes.loc[i, 'Código Estado / Departamento'] = maestroClientes['Código Estado / Departamento'][i][0:(len(maestroClientes['Código Estado / Departamento'][i])-2)]
        if len(maestroClientes['Código Estado / Departamento'][i])==1:
            maestroClientes.loc[i, 'Código Estado / Departamento'] = "0" + maestroClientes['Código Estado / Departamento'][i]
        i = i + 1

    formato['Código departamento/estado'] = maestroClientes['Código Estado / Departamento']
    formato['Código ciudad'] = maestroClientes['Código ciudad']
    formato['Teléfono principal'] = maestroClientes['CELULAR_TITULAR']
    formato['Tipo de régimen IVA'] = "0 - No responsable de IVA"
    formato['Código Responsabilidad fiscal'] = "R-99-PN"
    formato['Correo electrónico contacto principal'] = "facturacion@deltacredit.com.co"
    formato['Clientes'] = "SI"
    formato['Estado'] = "Activo"

    CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Subir Terceros desde Excel - Siigo Nube_CO_preliminar.xlsx", "codigosDepartamento", formato, False)
    
