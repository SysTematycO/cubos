import sys

sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Repositorios')
sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Servicios')
sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Asistencias')

import CRUD
import Cartera as ca
import Pagos as pa
import GeneracionSalidas as gs
import ConexionBD
import Direcciones

def DatosCubos(creditoFondeador, cubo, origen, destino):

    cartera.set_baseInfo(cubo)

    creditoFondeador = cartera.ObtenerDatosCubos(creditoFondeador, origen, destino)

    return creditoFondeador

conexionTecfinanzas = ConexionBD.ConexionBD(
    "nukak.tecfinanzas.com", "K003", "JCAMARGO", "JC4m4rg02022*")
cursorTecfinanzas = conexionTecfinanzas.ConexionBDSqlServer()

conexionTecfinanzasCopia = ConexionBD.ConexionBD(
    "nukak.tecfinanzas.com", "K003_2", "JCAMARGO", "JC4m4rg02022*")
cursorTecfinanzasCopia = conexionTecfinanzasCopia.ConexionBDSqlServer()

conexionDelta = ConexionBD.ConexionBD(
    "delta-db-core.database.windows.net", "Qatar", "deltavalidator", "Validator456@")
cursorDelta = conexionDelta.ConexionBDSqlServer()

CRUD.QueryRuta("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/ConsultasSQL/AplicacionPagos.sql", cursorTecfinanzas)
pagosCubos = CRUD.ReadSinRuta("SELECT * FROM AplicacionPagos", cursorTecfinanzasCopia)
CRUD.QuerySinRuta("DROP TABLE AplicacionPagos", cursorTecfinanzasCopia)

fondeadores = CRUD.ReadSinRuta("SELECT * FROM fondeadores", cursorDelta)

creditoFondeador = CRUD.Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/ConsultasSQL/CreditoFondeador.sql", cursorTecfinanzas)

carteraCubo = CRUD.LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Mensual/CarteraM.csv","|")

infoPersonas = CRUD.Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/ConsultasSQL/InformacionTitular.sql",cursorTecfinanzas)

garantiasCubo = CRUD.LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Historico/GarantiasH.csv","|")

garantiasCubo = garantiasCubo[(garantiasCubo['Tipo Garantia']=='Principal')]

pagos = pa.Pagos(fondeadores)

pagos = pagos.SegmentacionFondeador(pagosCubos)

cartera = ca.Cartera(fondeadores)

creditoFondeador = cartera.RenombrarFondeador(creditoFondeador)

origen = ['DIAS_VENCIDOS', 'EDAD_MORA_2']
destino = ['Dias en Mora', 'Edad Mora']

creditoFondeador = DatosCubos(creditoFondeador, carteraCubo, origen, destino)

origen = ['DIRECCION_TITULAR', 'BARRIO_TITULAR', 'CIUDAD_TITULAR', 'DEPARTAMENTO_TITULAR']
destino = ['Direccion', 'Barrio', 'Ciudad', 'Departamento']

creditoFondeador = DatosCubos(creditoFondeador, infoPersonas, origen, destino)
creditoFondeador['DIRECCION_TITULAR'] = Direcciones.EliminarEspaciosSobrantes(creditoFondeador, "DIRECCION_TITULAR")

origen = ['MARCA', 'PLACA', 'MODELO', 'CLASE']
destino = ['Marca', 'Placa', 'Modelo' , 'Clase']

creditoFondeador = DatosCubos(creditoFondeador, garantiasCubo, origen, destino)

cartera.set_baseInfo(fondeadores)
creditoFondeador = cartera.SegmentarFondeador(creditoFondeador)