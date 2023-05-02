from ConexionBD import *
import pandas as pd

def ConsultaSQL(sentenciaSql):
    conexion =  ConexionBDSqlServer()
    consulta = pd.read_sql_query(sentenciaSql,conexion)  
    return consulta

def LeerExcel(rutaValorFasecolda):
    base = pd.read_excel(rutaValorFasecolda)
    return base    

def LeerCsv(ruta,separador):
    base = pd.read_csv(ruta, sep = separador)
    return base

def LeerExcelConHoja(ruta, hoja):
    base = pd.read_excel(ruta, sheet_name = hoja)
    return base            
