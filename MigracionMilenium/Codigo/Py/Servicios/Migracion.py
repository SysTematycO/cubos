import sys
import time

sys.path.append(r'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/MigracionMilenium/Codigo/Py/Repositorios')

import requests
import pandas as pd
import GeneracionSalidas as gs
import numpy as np

class Migracion:
    
    def __init__(self, url, prstms):
        self._url = url 
        self._prstms = prstms

    def GetDatosBasicos(self, base):
        base_copy = base.copy()
        base_copy['IdPrestamo'] = base_copy['IdPrestamo'].astype(str)

        for i in range(len(base_copy)):
            if base_copy.at[i, 'IdPrestamo'].find(".") != -1:
                base_copy.at[i, 'IdPrestamo'] = base_copy.at[i, 'IdPrestamo'][:-2]
        return base
    
    """def GetDatosBasicos(self, base):

        base_copy = base.copy()
        
        for i in range(len(base_copy)):
            if (base_copy['NÚMERO DE CRÉDITO'][i] == '') | (pd.isna(base_copy['NÚMERO DE CRÉDITO'][i])):
                base_copy.loc[i, 'NÚMERO DE CRÉDITO'] = '0'

        base_copy['NÚMERO DE CRÉDITO'] = base_copy['NÚMERO DE CRÉDITO'].astype(int)
        self._prstms['Credito'] = self._prstms['Credito'].astype(int)

        base_copy = base_copy.merge(self._prstms, how='left' ,left_on='NÚMERO DE CRÉDITO', right_on='Credito')


        base_copy['Credito'] = base_copy['Credito'].astype(str)

        for i in range(len(base_copy)):
            if pd.isna(base_copy.at[i, 'Credito']):
                base_copy.at[i, 'Credito'] = ''
            elif base_copy.at[i, 'Credito'].find(".") != -1:
                base_copy.at[i, 'Credito'] = base_copy.at[i, 'Credito'][:-2]
  

        base_copy['CEDULA CLIENTE'] = base_copy['CEDULA CLIENTE'].astype(str)
        self._prstms['NDoc'] = self._prstms['NDoc'].astype(str)

        vehiculosProductivos = self._prstms.copy()
        vehiculosProductivos = vehiculosProductivos[(vehiculosProductivos['Producto']=='Consumo Vehiculos Productivos')]

        vaciosbase_copy = base_copy[(base_copy['NÚMERO DE CRÉDITO']==0)]
        base_copy = base_copy[(base_copy['NÚMERO DE CRÉDITO']!=0)]

        vaciosbase_copy = vaciosbase_copy.reset_index(drop=True)
        vehiculosProductivos = vehiculosProductivos.reset_index(drop=True)

        vaciosbase_copy = vaciosbase_copy.merge(vehiculosProductivos, how='left' ,left_on='CEDULA CLIENTE', right_on='NDoc')

        vaciosbase_copy['TDoc_x'] = vaciosbase_copy['TDoc_y']
        vaciosbase_copy['NDoc_x'] = vaciosbase_copy['NDoc_y']
        vaciosbase_copy['Credito_x'] = vaciosbase_copy['Credito_y']
        vaciosbase_copy['IdPrestamo_x'] = vaciosbase_copy['IdPrestamo_y']
        
        cols_y = vaciosbase_copy.filter(regex='_y', axis=1)
        cols_x = vaciosbase_copy.filter(regex='_x', axis=1)

        vaciosbase_copy = vaciosbase_copy.drop(cols_y.columns, axis=1)
        
        for i, col in enumerate(cols_x):
            vaciosbase_copy = vaciosbase_copy.rename(columns={col:col[:-2]})

        base_copy = pd.concat([base_copy, vaciosbase_copy], axis=0)
        base_copy = base_copy.reset_index(drop=True)

        base_copy['IdPrestamo'] = base_copy['IdPrestamo'].astype(str)

        for i in range(len(base_copy)):
            if pd.isna(base_copy.at[i, 'IdPrestamo']):
                base_copy.at[i, 'IdPrestamo'] = ''
            elif base_copy.at[i, 'IdPrestamo'].find(".") != -1:
                base_copy.at[i, 'IdPrestamo'] = base_copy.at[i, 'IdPrestamo'][:-2]
        
        base_copy = base_copy[(base_copy['IdPrestamo']!="")]
        base_copy = base_copy.sort_values(by=['IdPrestamo', 'FECHA GESTIÓN'], ascending=[True, True])
        base_copy = base_copy.reset_index(drop=True)

        return base_copy"""

         
    def EnvioGestionLlamadas(self, base):

        baseCopia = base.copy()
        baseCopia = self.GetDatosBasicos(baseCopia)
        i = 0
        while i < len(baseCopia):

            fecha_gestion = pd.to_datetime(baseCopia['FECHA GESTIÓN'][i])
            fecha_gestion_str = '1900-01-01T00:00:00.000Z' if pd.isna(fecha_gestion) else fecha_gestion.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'
            fecha_promesa = pd.to_datetime(baseCopia['FECHA DE LA PROMESA'][i])
            fecha_promesa_str = '1900-01-01T00:00:00.000Z' if pd.isna(fecha_promesa) else fecha_promesa.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'

            datos = {
                "idPrestamo": str(baseCopia['IdPrestamo'][i]),
                "ndoc": str(baseCopia['NOMBRE AGENTE'][i]),
                "tdoc": "1",
                "cobranza": {
                    "idCobranza": -1,
                    "fecha": fecha_gestion_str,
                    "fechaCompromiso": fecha_promesa_str,
                    "observacion": fecha_gestion_str if pd.isnull(baseCopia['OBSERVACIONES'][i]) else fecha_gestion_str + baseCopia['OBSERVACIONES'][i],
                    "tipo": "" if pd.isnull(baseCopia['TIPIFICACIÓN'][i]) else baseCopia['TIPIFICACIÓN'][i], 
                    "idTipo": 0 if pd.isnull(baseCopia['CODIGO TIPIFICACION'][i]) else int(baseCopia['CODIGO TIPIFICACION'][i]),
                    "nombres": "",
                    "generacion": "" if pd.isnull(baseCopia['SUB TIPIFICACIÓN 1'][i]) else baseCopia['SUB TIPIFICACIÓN 1'][i],
                    "idGeneracion": 0 if pd.isnull(baseCopia['CODIGO SUB TIPIFICACIÓN 1'][i]) else int(baseCopia['CODIGO SUB TIPIFICACIÓN 1'][i]),
                    "subtipo": "" if pd.isnull(baseCopia['SUB TIPIFICACIÓN 2'][i]) else baseCopia['SUB TIPIFICACIÓN 2'][i],
                    "idSubtipo": 0 if pd.isnull(baseCopia['CODIGO SUB TIPIFICACIÓN 2'][i]) else int(baseCopia['CODIGO SUB TIPIFICACIÓN 2'][i])
                }
            }
            try:
                requests.post(self._url, json=datos)
            except Exception as e:
                print("Error en la petición POST: " + str(e) + str(datos))
                time.sleep(1)
            i += 1