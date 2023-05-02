from LeerArchivo import *
import time
import pyautogui as pa
import keyboard

def ActualizarPowerBI(ruta, sleepAbrir, sleepActualizar):
    recaudo = AbrirArchivo(ruta)
    time.sleep(sleepAbrir)
    pa.click(x=655,y=98)#BotonActualizar
    time.sleep(sleepActualizar)
    pa.click(x=1343,y=16)#BotonCerrar
    time.sleep(2.5)
    pa.click(x=691,y=404)#BotonCerrar-Aceptar
    time.sleep(2.5)

#Historicos
def Ejecutar(ejecucion):
    if ejecucion == True:
        powerBi = ['C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/OriginacionH.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/RecaudoH.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/CarteraH.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/GeneralH.pbix']

        i=0
        while i < len(powerBi):
            ActualizarPowerBI(powerBi[i],30, 40)
            i = i + 1
    else:
        #Mensuales
        powerBi = ['C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/OriginacionM.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/RecaudoM.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/CarteraM.pbix',
        'C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/PBI/MENSUALES/GeneralM.pbix']

        i=0
        while i < len(powerBi):
            ActualizarPowerBI(powerBi[i],35, 150)
            i = i + 1