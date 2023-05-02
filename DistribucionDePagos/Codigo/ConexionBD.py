import pyodbc 
import pywin32_system32 as win32

servidor = 'nukak.tecfinanzas.com'
bdDatos = 'K003'
usuario = 'JCAMARGO'
clave = 'JC4m4rg02022*'  

def ConexionBDSqlServer():
    try:
        conexion = pyodbc.connect('DRIVER={SQL Server};SERVER='+servidor+
        ';DATABASE='+bdDatos+';UID='+usuario+';PWD='+clave)
    except:
        print ("Error de conexion")

    return conexion





