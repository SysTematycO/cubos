from ConexionBD import *
import pandas as pd

def ConsultaSQL(sentenciaSql):
    conexion =  ConexionBDSqlServer()
    consulta = pd.read_sql_query(sentenciaSql,conexion)  
    return consulta

