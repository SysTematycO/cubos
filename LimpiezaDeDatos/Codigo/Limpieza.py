import pandas as pd
from LeerConsultas import *
from CRUD import *
from ConexionBD import *

def ObtenerSolicitud(base):
    prestamos = Read("SELECT ctivo AS 'CREDITO', solicitud FROM prstms WHERE IdTipoPrestamo = 'PFIJA'")
    base = pd.merge(base, prestamos, how="inner", on=["CREDITO"])
    return base

def QueryUpdateGarantias(valor, descripcion, idCaptura, solicitud):
    query = "UPDATE valorescapturasdinamicas SET valor = '" + valor + "' WHERE Descripcion = '"+ descripcion +"' AND IdCaptura = '"+ idCaptura +"' AND NoProducto = '" + solicitud + "'"
    EjecutarQuery(query, cursor)

def ActualizarGarantiasBD(base):
    contador = 0
    while contador < len(base):
        QueryUpdateGarantias(base['Linea_De_Credito'][contador], "Linea_De_Credito", base['IdCaptura'][contador], base['solicitud'][contador])
        QueryUpdateGarantias(base['Capacidad_KG_PSJ'][contador], "Capacidad_KG_PSJ", base['IdCaptura'][contador], base['solicitud'][contador])  
        QueryUpdateGarantias(str(base['Fasecolda_Codigo'][contador]), "Fasecolda_Codigo", base['IdCaptura'][contador], base['solicitud'][contador])
        QueryUpdateGarantias(str(base['Tipo_Carroceria'][contador]), "Tipo_Carroceria", base['IdCaptura'][contador], base['solicitud'][contador])  
        QueryUpdateGarantias(str(base['Fasecolda_Marca'][contador]), "Fasecolda_Marca", base['IdCaptura'][contador], base['solicitud'][contador])  
        QueryUpdateGarantias(str(base['Fasecolda_Linea'][contador]), "Fasecolda_Linea", base['IdCaptura'][contador], base['solicitud'][contador])  
        QueryUpdateGarantias(str(base['Fasecolda_Clase'][contador]), "Fasecolda_Clase", base['IdCaptura'][contador], base['solicitud'][contador])
        QueryUpdateGarantias(str(base['Fasecolda_Modelo'][contador]), "Fasecolda_Modelo", base['IdCaptura'][contador], base['solicitud'][contador])    
        contador = contador + 1

cursor = ConexionBDSqlServer().cursor()
informacion = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/LimpiezaDeDatos/Codigo/Entradas/CARGUE INF TECFI.xlsx")
informacion = ObtenerSolicitud(informacion)
ActualizarGarantiasBD(informacion)
