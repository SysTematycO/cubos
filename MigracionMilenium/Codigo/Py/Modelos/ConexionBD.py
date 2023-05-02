import pyodbc 

class ConexionBD:

    conexion = ''
    
    def __init__(self, servidor, bd, usuario, clave):
        self.servidor = servidor
        self.bd = bd
        self.usuario = usuario
        self.clave = clave

    def ConexionBDSqlServer(self):
        try:
            conexion = pyodbc.connect('DRIVER={SQL Server};SERVER='+self.servidor+
            ';DATABASE='+self.bd+';UID='+self.usuario+';PWD='+self.clave)
        except:
            print ("Error de conexion")
        return conexion





