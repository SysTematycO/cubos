from LeerConsultas import *
from GeneracionSalidas import *

def QuitarCeros(base,nombreCampo,inicio,final):
    contador = 0
    base[nombreCampo] = base[nombreCampo].astype(str)
    while contador < len (base):
        if '.' in base[nombreCampo][contador]:
            base[nombreCampo][contador] = base[nombreCampo][contador][inicio:len(base[nombreCampo][contador])-final]
        contador = contador + 1
    return base 

actividades = LeerExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DatosLocal/Codigo/Entradas/Actualizacion inf actividades 2.0.xlsx")

originacion = LeerCsv("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/Bodega De Datos/DATA/Reportes/Historico/OriginacionH.csv","|")

actividades['CREDITO'] = actividades['CREDITO'].astype(str)
originacion['Credito'] = originacion['Credito'].astype(str)

actividades = actividades.merge(originacion, left_on='CREDITO', right_on='Credito', how="left")

consulta = ConsultaSQL("""SELECT p.Ctivo AS 'CREDITO', v.Valor AS 'TiempoSector'  FROM valorescapturasdinamicas v
LEFT JOIN (SELECT * FROM prstms WHERE IdTipoPrestamo = 'PFIJA') p ON v.NDocUsuario = p.Ndoc
WHERE idcaptura = 'UT_NTiempoSector' AND p.NDoc IS NOT NULL
GROUP BY p.Ctivo, v.Valor
ORDER BY p.Ctivo
""")

consulta['CREDITO'] = consulta['CREDITO'].astype(str)

consulta = QuitarCeros(consulta,"CREDITO",0,2)

actividades = actividades.merge(consulta, left_on='CREDITO', right_on='CREDITO', how="left")

consulta = ConsultaSQL("""SELECT p.Ctivo AS 'CREDITO', v.Valor AS 'QuienManeja'  FROM valorescapturasdinamicas v
LEFT JOIN (SELECT * FROM prstms WHERE IdTipoPrestamo = 'PFIJA') p ON v.NDocUsuario = p.Ndoc
WHERE idcaptura = 'UT_OCQuienM' AND p.NDoc IS NOT NULL AND v.Valor <> '' AND v.Valor <> '0'
GROUP BY p.Ctivo, v.Valor
ORDER BY p.Ctivo""")

consulta['CREDITO'] = consulta['CREDITO'].astype(str)

consulta = QuitarCeros(consulta,"CREDITO",0,2)

actividades = actividades.merge(consulta, left_on='CREDITO', right_on='CREDITO', how="left")

consulta = ConsultaSQL("""SELECT p.Ctivo AS 'CREDITO', v.Valor AS 'Transp'  FROM valorescapturasdinamicas v
LEFT JOIN (SELECT * FROM prstms WHERE IdTipoPrestamo = 'PFIJA') p ON v.NDocUsuario = p.Ndoc
WHERE idcaptura = 'UT_EXPActividad' AND p.NDoc IS NOT NULL AND v.Valor <> '' AND v.Valor <> '0'
GROUP BY p.Ctivo, v.Valor
ORDER BY p.Ctivo""")

consulta['CREDITO'] = consulta['CREDITO'].astype(str)

consulta = QuitarCeros(consulta,"CREDITO",0,2)

actividades = actividades.merge(consulta, left_on='CREDITO', right_on='CREDITO', how="left")

consulta = ConsultaSQL("""SELECT p.Ctivo AS 'CREDITO', v.Valor AS 'Taxis'  FROM valorescapturasdinamicas v
LEFT JOIN (SELECT * FROM prstms WHERE IdTipoPrestamo = 'PFIJA') p ON v.NDocUsuario = p.Ndoc
WHERE idcaptura = 'UT_EXPTaxis' AND p.NDoc IS NOT NULL AND v.Valor <> '' AND v.Valor <> '0'
GROUP BY p.Ctivo, v.Valor
ORDER BY p.Ctivo""")

consulta['CREDITO'] = consulta['CREDITO'].astype(str)

consulta = QuitarCeros(consulta,"CREDITO",0,2)

actividades = actividades.merge(consulta, left_on='CREDITO', right_on='CREDITO', how="left")

actividades['OCUPACION '] = ""
actividades['PROFESION '] = ""
actividades['TIPO DE EXP '] = ""
actividades['SECT TRANSP '] = ""
actividades['TIEMPO ( MESES ) '] = ""
actividades['QUIEN VA A MANEJAR '] = ""

actividades['OCUPACION '] = actividades['Actividad Cliente']
actividades['PROFESION '] = actividades['Profesion']
actividades['TIPO DE EXP '] = actividades['Tipo de Experiencia']
actividades['TIEMPO ( MESES ) '] = actividades['TiempoSector']
actividades['QUIEN VA A MANEJAR '] = actividades['QuienManeja']
actividades['SECT TRANSP '] = actividades['Transp']
actividades['SECT TAXIS'] = actividades['Taxis']

actividades = actividades[['CREDITO','OCUPACION ','PROFESION ','SECT TAXIS','SECT TRANSP ','TIPO DE EXP ','TIEMPO ( MESES ) ','QUIEN VA A MANEJAR ']]

CrearTXT("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/DatosLocal/Salidas/Actualizacion inf actividades 2.0.csv", "|", actividades, False)
