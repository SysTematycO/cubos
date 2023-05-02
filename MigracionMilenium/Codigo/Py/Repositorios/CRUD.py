from LeerConsultas import *

def QueryRuta(ruta, cursor):
    with open(ruta) as file_object:
        query = file_object.read() 
        cursor.execute(query)
        cursor.commit()

def QuerySinRuta(query, cursor):
    cursor.execute(query)
    cursor.commit()

def Read(ruta, cursor):
    with open(ruta) as file_object:
        query = file_object.read() 
        datos = ConsultaSQL(query,cursor)
    return datos

def ReadSinRuta(query, cursor):
    datos = ConsultaSQL(query, cursor)
    return datos