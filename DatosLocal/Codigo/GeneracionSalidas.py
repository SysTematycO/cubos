import pandas as pd

def CrearTXT(ruta, separador, pivot, validacionIndex):    
    pivot.to_csv(ruta, sep = separador, index = validacionIndex, encoding = "utf-8-sig")
