import sys

sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Repositorios')
sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Asistencias')

import LeerConsultas
import GeneracionSalidas as gs
import CRUD
import datetime
import locale
import os
import TransformacionDatos as td
import shutil

class Pagos:
    
    def __init__(self, baseInfo):
        self._baseInfo = baseInfo

    def get_baseInfo(self):
        return self._baseInfo
      
    def set_baseInfo(self, value):
        self._baseInfo = value
        
    def SegmentacionFondeador(self, pagos):

        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

        ultimaFechaMesAnterior = datetime.date.today().replace(day=1) + datetime.timedelta(days=-1)

        mesLetra = ultimaFechaMesAnterior.strftime("%B").capitalize()

        anioNumero = ultimaFechaMesAnterior.year

        rutaInicial = "C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/REPORTES FONDEADOR/DATA/MENSUAL/" + mesLetra + " " + str(anioNumero)

        if os.path.exists(rutaInicial) == False:
            os.mkdir(rutaInicial)
        else:
            shutil.rmtree(rutaInicial)
            os.mkdir(rutaInicial)
                
        i = 0
        while i < len(self._baseInfo):

            segmentacion = pagos[(pagos['CUENTA_RECAUDO'] ==
                                self._baseInfo['Fondeador'][i])]

            ruta = rutaInicial + "/" + self._baseInfo['NombreAsociado'][i] + ".xlsx"

            columnasInt = ['CREDITO', 'CONSECUTIVO']
            
            if os.path.exists(ruta):
                
                baseConcantenar = LeerConsultas.LeerExcelConHoja(ruta, "pagos")

                segmentacion = td.ConcatenarBases(segmentacion, baseConcantenar)

                segmentacion = td.CambiarTipoFecha(segmentacion, "FECHA_APLICACION")
                segmentacion = td.CambiarTipoFecha(segmentacion, "FECHA_PAGO")

                segmentacion = segmentacion.sort_values('FECHA_PAGO')

                segmentacion = segmentacion.reset_index(drop=True)

                segmentacion = td.ConvertirInt(segmentacion, columnasInt)

                gs.CrearExcel(ruta, "pagos", segmentacion, False)
            
            elif segmentacion.empty == False:

                segmentacion = td.CambiarTipoFecha(segmentacion, "FECHA_APLICACION")
                segmentacion = td.CambiarTipoFecha(segmentacion, "FECHA_PAGO")

                segmentacion = segmentacion.sort_values('FECHA_PAGO')

                segmentacion = segmentacion.reset_index(drop=True)

                segmentacion = td.ConvertirInt(segmentacion, columnasInt)

                gs.CrearExcel(ruta, "pagos", segmentacion, False)
                
            i += 1