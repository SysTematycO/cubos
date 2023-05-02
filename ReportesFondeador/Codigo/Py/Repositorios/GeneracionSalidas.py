import pandas as pd

def CrearExcel(ruta, hoja, pivot, validacionIndex):
    writer = pd.ExcelWriter(ruta)
    pivot.to_excel(writer,hoja, index = validacionIndex)
    writer.close()

def CrearTXT(ruta, separador, pivot, validacionIndex):    
    pivot.to_csv(ruta, sep = separador, index = validacionIndex, encoding = "utf-8-sig")

def CrearExcelHojas(ruta, hojas, bases, validacionIndex):
    with pd.ExcelWriter(ruta, engine='xlsxwriter') as writer:
        for i, df in enumerate(bases):
            df.to_excel(writer, sheet_name=hojas[i], index=validacionIndex)