from datetime import datetime
from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from datetime import datetime

cursor = ConexionBDSqlServer().cursor()

def ActualizarFecha():
    fecha = datetime.today()
    fecha = fecha.strftime('%d/%m/%Y')
    cursor.execute("UPDATE ConsecutivoAutomatizaciones SET UltimaFecha = '" + fecha + "' WHERE TipoArchivo = 'AplicacionPagos'")
    cursor.commit()

ActualizarFecha()

