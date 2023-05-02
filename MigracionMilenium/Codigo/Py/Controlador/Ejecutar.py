import sys

sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/MigracionMilenium/Codigo/Py/Repositorios')
sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/MigracionMilenium/Codigo/Py/Servicios')

import LeerConsultas as lc
import CRUD as c
import ConexionBD
import os
import Migracion as mi

conexionTecfinanzas = ConexionBD.ConexionBD(
    "nukak.tecfinanzas.com", "K003", "JCAMARGO", "JC4m4rg02022*")
cursorTecfinanzas = conexionTecfinanzas.ConexionBDSqlServer()

prstms = c.Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/MigracionMilenium/Codigo/Consultas/IdPrestamo.sql",cursorTecfinanzas)

migracion = mi.Migracion("https://nukak.tecfinanzas.com/TFMPrestamos/PRSTMS/cobranza/DELTA", prstms)

ruta_archivo = "C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/MigracionMilenium/Entradas/BaseMilenium.xlsx"
base = lc.LeerExcel(ruta_archivo)
migracion.EnvioGestionLlamadas(base)

