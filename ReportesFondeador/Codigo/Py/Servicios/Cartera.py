import sys
import pandas as pd

sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Repositorios')
sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReportesFondeador/Codigo/Py/Asistencias')

import LeerConsultas as lc
import GeneracionSalidas as gs
import locale
import datetime
import os
import TransformacionDatos as td

class Cartera:
    
    def __init__(self, baseInfo):
        self._baseInfo = baseInfo

    def get_baseInfo(self):
        return self._baseInfo
      
    def set_baseInfo(self, value):
        self._baseInfo = value

    def RenombrarFondeador(self, creditoFondeador):

        creditoFondeador = creditoFondeador.merge(
        self._baseInfo, how="left", left_on="NOMBRE_FONDEADOR", right_on="FondeadorTecfinanzas")
    
        for i in range(len(creditoFondeador)):
            if pd.isna(creditoFondeador['FondeadorTecfinanzas'][i])==False:
                creditoFondeador['NOMBRE_FONDEADOR'][i] = creditoFondeador['NombreAsociado'][i]

        creditoFondeador = creditoFondeador.drop(self._baseInfo.columns, axis=1)

        creditoFondeador = creditoFondeador[creditoFondeador.columns].drop_duplicates()

        creditoFondeador = creditoFondeador.reset_index(drop=True)

        return creditoFondeador

    def ObtenerDatosCubos(self, creditoFondeador, origen, destino):
        
        creditoFondeador['NoCREDITO'] = creditoFondeador['NoCREDITO'].astype(int)
        self._baseInfo['Credito'] = self._baseInfo['Credito'].astype(int)

        creditoFondeador = creditoFondeador.merge(
        self._baseInfo, how="left", left_on="NoCREDITO", right_on="Credito")

        for i in range(len(origen)):
            creditoFondeador[origen[i]] = self._baseInfo[destino[i]]
        
        creditoFondeador = creditoFondeador.drop(self._baseInfo.columns, axis=1)

        creditoFondeador = creditoFondeador[creditoFondeador.columns].drop_duplicates()

        creditoFondeador = creditoFondeador.reset_index(drop=True)

        return creditoFondeador

    def SegmentarFondeador(self, creditoFondeador):
        
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

        ultimaFechaMesAnterior = datetime.date.today().replace(day=1) + datetime.timedelta(days=-1)

        mesLetra = ultimaFechaMesAnterior.strftime("%B").capitalize()

        anioNumero = ultimaFechaMesAnterior.year

        rutaInicial = "C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/REPORTES FONDEADOR/DATA/MENSUAL/" + mesLetra + " " + str(anioNumero)

        columnasInt = ['NoCREDITO']

        for i in range(len(self._baseInfo)):
            segmentacion = creditoFondeador[(creditoFondeador['NOMBRE_FONDEADOR'] ==
                                self._baseInfo['NombreAsociado'][i])]

            ruta = rutaInicial + "/" + self._baseInfo['NombreAsociado'][i] + ".xlsx"

            if os.path.exists(ruta):

                basePagos = lc.LeerExcelConHoja(ruta, "pagos")
                segmentacion = td.ConvertirInt(segmentacion, columnasInt)

                segmentacion = segmentacion.drop(['NOMBRE_FONDEADOR'], axis=1)

                bases = [basePagos, segmentacion]
                hojas = ["pagos", "cartera"]
                
                gs.CrearExcelHojas(ruta, hojas, bases, False)

            elif segmentacion.empty == False:    
                
                segmentacion = td.ConvertirInt(segmentacion, columnasInt)
                segmentacion = segmentacion.drop(['NOMBRE_FONDEADOR'], axis=1)

                bases = [segmentacion]
                hojas = ["cartera"]

                gs.CrearExcelHojas(ruta, hojas, bases, False)