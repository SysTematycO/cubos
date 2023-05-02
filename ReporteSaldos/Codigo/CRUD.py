from LeerConsultas import *

def Create(ruta, cursor):
    with open(ruta) as file_object:
        query = file_object.read() 
        cursor.execute(query)
        cursor.commit()

def Delete(ruta, cursor):
     with open(ruta) as file_object:
        query = file_object.read() 
        cursor.execute(query)
        cursor.commit()

def Read(ruta):
    with open(ruta) as file_object:
        query = file_object.read() 
        datos = ConsultaSQL(query)
    return datos