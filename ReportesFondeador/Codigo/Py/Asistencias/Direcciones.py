def EliminarEspaciosSobrantes(dataFrame,columna):

    datos = dataFrame[columna].str.strip()

    cadenaGuardada = ""
    quitarEspacio = True
    caracterAnterior = False 

    i = 0
    j = 0

    while i < len (datos):
        direccion = datos[i]

        while j < len (direccion):
            if direccion[j] == " ":
                if direccion[j+1] == " ":
                    quitarEspacio = False
            if direccion[j-1] != " ":
                caracterAnterior = True
            if quitarEspacio == True | caracterAnterior == True:
                cadenaGuardada += direccion[j]

            quitarEspacio = True
            caracterAnterior = False    
            j += 1
            
        dataFrame[columna][i] = cadenaGuardada
        cadenaGuardada = ""    
        j = 0
        i += 1

    return dataFrame[columna]