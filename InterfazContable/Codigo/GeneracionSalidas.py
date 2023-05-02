import pandas as pd

def CrearExcel(ruta, hoja, pivot, validacionIndex):    
    writer = pd.ExcelWriter(ruta)
    pivot.to_excel(writer,hoja, index = validacionIndex)
    writer.close()

def CrearTXT(ruta, separador, pivot, validacionIndex):    
    pivot.to_csv(ruta, sep = separador, index = validacionIndex, encoding = "utf-8-sig")
