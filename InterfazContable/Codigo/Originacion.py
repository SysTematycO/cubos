import pandas as pd
import numpy as np

from LeerConsultas import *
from GeneracionSalidas import *
from ConexionBD import *
from MaestroClientes import *
from CRUD import *
from datetime import datetime


def Repeticiones(nombreCampo):
    l = 0
    repeticion = [1 if val != 0 else l for val in datos[nombreCampo]]
    return repeticion

def ParticionCreditos(datos):
    campos = ['CAPITAL INICIAL','RUNT','GARANTIAS M','IVA GM','CXC INTERESES INICIALES','CXC VALOR TOTAL PERIODO DE GRACIA']
    i = 0
    rep = 0
    while i < len(campos):
        rep = len (Repeticiones(campos[i])) + rep
        i += 1

    rep = rep / len(datos["CEDULA"]) * 2
    datos = datos.loc[np.repeat(datos.index.values,rep)]
    datos = np.array_split(datos, len (datos) / rep)

    i = 0
    while i < len (datos):
        datos[i] = datos[i].reset_index(drop=True)
        datos[i] = pd.concat([datos[i], cuentaContable], axis=1)
        i += 1

    i = 0
    while i < len (datos):
        if i == 0:
            base = datos[i]
        if i > 0:    
            base = pd.concat([datos[i],base])
        i += 1

    return base 

def ActualizarPartidas(base):

    concepto = ['CAPITAL INICIAL','CXP CLIENTE','RUNT','INGRESO RUNT','GARANTIAS M','INGRESO GM','IVA GM','INGRESO GM IVA',
    'CXC INTERESES INICIALES','INGRESO INT INICIALES','CXC VALOR TOTAL PERIODO DE GRACIA','INTERESES PERIODO DE GRACIA']
    partida = ['Debito','Crédito']

    i = 0
    while i < len(concepto):
        if((i%2)==0):   
            base.loc[base['Concepto'] == concepto[i], partida[i%2]] = base[concepto[i]][i]
        else:
            base.loc[base['Concepto'] == concepto[i], partida[i%2]] = base[concepto[i-1]][i]     
        i += 1

    base.loc[base['Debito'].isnull(), 'Debito'] = 0
    base.loc[base['Crédito'].isnull(), 'Crédito'] = 0

    base = base.reset_index(drop=True)
    base = base.drop(base[(base['Debito']==0) & (base['Crédito']==0)].index)

    base['MES'] = pd.DatetimeIndex(base['FECHA ORIGINACION']).month
    base = base.merge(meses, left_on='MES', right_on='MesNum')

    
    return base

def LlenarFormato(formato, base, consecutivo):

    formato['Débito'] = base['Debito']
    formato['Crédito'] = base['Crédito']
    formato['Código cuenta contable'] = base['cuenta contable']
    formato['Identificación tercero'] = base['CEDULA']
    formato['Descripción'] = "ORIGINACIÓN " + base['NoCREDITO']
    formato['Tipo de comprobante'] = 100

    formato['Consecutivo comprobante'] = consecutivo

    fecha = datetime.today()
    fecha = fecha.strftime('%d/%m/%Y')

    formato['Fecha de elaboración '] = fecha
    formato['Observaciones'] = "ORIGINACIÓN " + base['MesLetra']

    return formato

def InstalacionGps(formato, nCuenta):

    creditosGps = ReadSinRuta("""SELECT CONVERT(VARCHAR(50), p.ctivo) AS 'Credito', CONVERT(VARCHAR(50), p.IdPrestamo) AS 'IdPrestamo', Valor AS 'Valor'
    FROM PrestamosCargos pc WITH(NOLOCK)
    INNER JOIN Prstms p WITH(NOLOCK) ON pc.IdPrestamo = p.IdPrestamo
    WHERE pc.TipoCargo = 'ADMIN' AND pc.Nombre = 'CGPS' AND pc.Valor != '0'""")
    
    capitalInicial = ReadSinRuta("""SELECT CONVERT(VARCHAR(50), p.ctivo) AS 'Credito', p.CapitalInicial AS 'Capital Inicial' FROM Prstms p""")

    formato['Credito'] = formato['Descripción']
    formato['Credito'] = formato['Credito'].astype(str)

    i = 0
    while i < len(formato):
        formato.loc[i, 'Credito'] = formato['Credito'][i][12:]
        i += 1

    creditosGps['Credito'] = creditosGps['Credito'].astype(str)
   
    creditosSinGps = formato.merge(creditosGps, on='Credito', how='left')
    creditosSinGps = creditosSinGps[(pd.isna(creditosSinGps['IdPrestamo']))]
    creditosSinGps = creditosSinGps.reset_index(drop = True)

    creditosGps = formato.merge(creditosGps, on='Credito', how='inner')

    creditosGps = creditosGps.drop(['IdPrestamo'], axis = 1)
    creditosSinGps = creditosSinGps.drop(['IdPrestamo'], axis = 1)

    concatenar = creditosGps
    concatenar = concatenar.iloc[0:0]
    
    if len(creditosGps) > 0:
        segmentacion = np.array_split(creditosGps, len(creditosGps))

        i = 0
        while i < len(segmentacion):
            j = 0
            tamanio = len(segmentacion[i])
            while j < tamanio:
                segmentacion[i] = segmentacion[i].reset_index(drop = True)
                if segmentacion[i]['Código cuenta contable'][j] == 13050501:
                    segmentacion[i] = segmentacion[i].merge(capitalInicial, on='Credito', how='inner')
                    segmentacion[i].loc[j, 'Débito'] = segmentacion[i]['Capital Inicial'][j]
                    segmentacion[i] = segmentacion[i].drop(['Capital Inicial'], axis = 1)

                    new_row = pd.DataFrame({
                        'Tipo de comprobante': [100],
                        'Consecutivo comprobante': [segmentacion[i]['Consecutivo comprobante'][j]],
                        'Fecha de elaboración ': [segmentacion[i]['Fecha de elaboración '][j]],
                        'Código cuenta contable': [nCuenta],
                        'Identificación tercero': [segmentacion[i]['Identificación tercero'][j]],
                        'Descripción': [segmentacion[i]['Descripción'][j]],
                        'Débito': [0],
                        'Crédito': [segmentacion[i]['Valor'][j]],
                        'Observaciones': [segmentacion[i]['Observaciones'][j]]
                    })
                    segmentacion[i] = pd.concat([segmentacion[i], new_row], ignore_index=True)

                concatenar = pd.concat([concatenar,segmentacion[i]], axis=0)
                j += 1
            i += 1

    concatenar = pd.concat([concatenar,creditosSinGps], axis=0)
    concatenar = concatenar.drop(['Credito','Valor'], axis = 1)

    return concatenar

def Consecutivo():
    #Cuando tengamos la BD propia
    return consecutivo["Consecutivo"][0]

cursor = ConexionBDSqlServer().cursor()

formato = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Formato interfaz contable (Encabezado).xlsx")
cuentaContable = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Cuentas contables SIIGO.xlsx")
meses = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Entradas/Meses.xlsx")

Create("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/DesembolsosCartera.sql", cursor)
datos = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/DesembolsosCarteraSELECT.sql")
DeleteSinRuta("DROP TABLE DesembolsoCartera",cursor)

base = ParticionCreditos(datos)
base = ActualizarPartidas(base)

print("Consecutivo: ")
consecutivo = input()
formato = LlenarFormato(formato, base, consecutivo)

baseOrignacion = formato
baseOrignacion['NoCredito'] = base['NoCREDITO']

formato = formato.drop(['NoCredito'], axis=1)

formato = InstalacionGps(formato, 28151008)

CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Salidas/Originacion.xlsx", "Originacion", formato, False)

#MAIN MAESTROCLIENTES/////////////////////////////////////////////////////////////
Create("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/MaestroClientes.sql", cursor)
maestroClientes = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/InterfazContable/Codigo/Consultas/MaestroClientesSELECT.sql")
DeleteSinRuta("DROP TABLE MAESTROCLIENTES",cursor)

maestroClientes = CruceOriginacionMaestro(baseOrignacion,maestroClientes)
LlenarFormatoMaestroClientes(maestroClientes)
#/////////////////////////////////////////////////////////////////

