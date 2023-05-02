from LeerConsultas import *

def EjecutarQuery(query, cursor):
    cursor.execute(query)
    cursor.commit()

def Read(query):
    datos = ConsultaSQL(query)
    return datos