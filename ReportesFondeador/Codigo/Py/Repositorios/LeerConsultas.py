import sys

sys.path.append(r'C:\Users\Jhon Camargo\OneDrive - Deltacredit S.A.S\DBA\Automatizaciones\ReportesFondeador\Codigo\Py\Modelos')

import ConexionBD
import pandas as pd

def ConsultaSQL(sentenciaSql, cursor):
    consulta = pd.read_sql_query(sentenciaSql,cursor)  
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
