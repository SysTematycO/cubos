import pyodbc 
import pandas as pd
from LogicaDesarrollo import *

servidor = 'nukak.tecfinanzas.com'
bdDatos = 'K003'
usuario = 'JCAMARGO'
clave = 'JC4m4rg02022*'  

conexion = pyodbc.connect('DRIVER={SQL Server};SERVER='+servidor+
        ';DATABASE='+bdDatos+';UID='+usuario+';PWD='+clave)

cursor = conexion.cursor()

def Pivot(segmentacionFecha):
    pivot = pd.pivot_table(datos,index=['CATEGORIA'],values=['GASTOS_DE_COBRANZA','IVAGAC','MORA','RUNT','GARANTIAS_MOBILIARIAS',
    'IVA_GARANTIAS_MOBILIARIAS','SEGURO','CXCPGRACIA','I_INICALES','KFACTURADO_VENCIDO','KFACTURADO_NO_VENCIDO',
    'KNO_FACTURADO','IFACTURADO','IVENCIDO'],columns=segmentacionFecha,aggfunc='sum')
    return pivot

def CrearExcel(ruta, hoja, pivot):    
    writer = pd.ExcelWriter(ruta)
    pivot.to_excel(writer,hoja)
    writer.save()

with open("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DistribucionDePagos/Codigo/ConsultasSQL/DistribucionDePagos.sql") as file_object:
    query= file_object.read() 
    cursor.execute(query)
    conexion.commit()

with open("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DistribucionDePagos/Codigo/ConsultasSQL/DistribucionDePagoBancos.sql") as file_object:
    query= file_object.read() 
    datos = ConsultaSQL(query)

    cursor.execute("DROP TABLE DistribucionDePagos")
    conexion.commit()

    pivot = Pivot("MESAÑO")
    pivot = pivot.transpose()

    pivotDetalle = Pivot("FECHA_APLICACION")
    pivotDetalle = pivotDetalle.transpose()

    #CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DistribucionDePagos/Salidas/DistribucionDePagos.xlsx","Distribucion",pivot)
    #CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DistribucionDePagos/Salidas/DistribucionDePagosDetalle.xlsx","Detalle",pivotDetalle) 

    


    

