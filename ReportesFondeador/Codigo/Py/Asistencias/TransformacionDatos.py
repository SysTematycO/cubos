import pandas as pd

def ConcatenarBases(baseUno, baseDos):

    baseUno = pd.concat([baseUno, baseDos], axis=0)

    return baseUno


def CambiarTipoFecha(base, columna):

    base[columna] = pd.to_datetime(base[columna], format='%Y-%m-%d')
    base[columna] = base[columna].apply(lambda x: x.date())

    return base


def ConvertirInt(base, columna):

    i = 0
    while i < len(columna):
        base[columna[i]] = base[columna[i]].astype(int)
        i += 1

    return base
