import pandas as pd

def CrearExcel(ruta, hoja, pivot, validacionIndex):    
    writer = pd.ExcelWriter(ruta)
    pivot.to_excel(writer,hoja, index = validacionIndex)
    writer.save()
