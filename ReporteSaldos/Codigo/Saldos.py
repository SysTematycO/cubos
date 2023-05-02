from GeneracionSalidas import *
from CRUD import *

filasEliminar = []
filasAgregar = []

def Merge(baseTotal, baseJoin):
    baseTotal = baseTotal.merge(baseJoin, how="left", on=["CREDITO", "FechaEfectiva"])
    return baseTotal

def OrdenarValores(baseTotal):

    contadorBaseTotal = 0
    auxiliar = 0
    
    while contadorBaseTotal < 1:
        contadorColumnas = 0
        fechaEfectiva = baseTotal['FechaEfectiva'][contadorBaseTotal]
        credito = baseTotal['CREDITO'][contadorBaseTotal]
        if contadorBaseTotal > 0:
            if credito != baseTotal['CREDITO'][contadorBaseTotal-1]:
                auxiliar = contadorBaseTotal
                filasAgregar.append(baseTotal.index[contadorBaseTotal])         
            else:
                if fechaEfectiva != baseTotal['FechaEfectiva'][contadorBaseTotal-1]:
                    auxiliar = contadorBaseTotal
                    filasAgregar.append(baseTotal.index[contadorBaseTotal])
                else:
                    filasEliminar.append(baseTotal.index[contadorBaseTotal])
        else:
            auxiliar = contadorBaseTotal
            filasAgregar.append(baseTotal.index[contadorBaseTotal]) 
        while contadorColumnas < len(baseTotal.columns):
            if baseTotal.columns[contadorColumnas] == baseTotal['Concepto'][contadorBaseTotal]:
                baseTotal[baseTotal.columns[contadorColumnas]][auxiliar] = baseTotal['Debito'][contadorBaseTotal]
            contadorColumnas = contadorColumnas + 1 
        contadorBaseTotal = contadorBaseTotal + 1 
    print ("1")
    return baseTotal

"""def EliminarFilasSobrantes(baseTotal, index):

    contadorIndex = 0
    while contadorIndex < len (index):   
        baseTotal = baseTotal.drop(index[contadorIndex])
        contadorIndex = contadorIndex + 1        
    print ("2")     
    return baseTotal"""

def AgregarFilas(baseTotal, index):

    base = pd.DataFrame(index=range(5))  
    #base.columns = baseTotal.columns
    print (len(base))
    print (base.columns)
    return base

cursor = ConexionBDSqlServer().cursor()  

baseTotal = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/BaseTotalSELECT.sql")

Create("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/AmortizacionVariableCausacion.sql", cursor)
amortizacion = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/AmortizacionVariableCausacionSELECT.sql")
Delete("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/AmortizacionVariableCausacionDROP.sql", cursor)

Create("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/ContaDetalleCausacion.sql", cursor)
contaDetalle = Read("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/ContaDetalleCausacionSELECT.sql")
Delete("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Codigo/ConsultasSQL/ContaDetalleCausacionDROP.sql", cursor)
        
baseTotal['CXC INTERES CORRIENTE'] = "0"
baseTotal['CXC SEGURO'] = "0"
baseTotal['INTERESES POR DIFERIR PERIODO DE GRACIA'] = "0"
baseTotal['BUSURA'] = "0"
baseTotal['GAC'] = "0"
baseTotal['IVAGAC'] = "0"
baseTotal['IMORA'] = "0"

baseTotal = Merge(baseTotal, contaDetalle)
baseTotal = OrdenarValores(baseTotal)
baseTotal = AgregarFilas(baseTotal,filasAgregar)
#baseTotal = EliminarFilasSobrantes(baseTotal, filasEliminar)

baseTotal = baseTotal.drop(['IdDiario', 'IdPrestamo','Valor','Debito', 'Concepto'], axis=1)

baseTotal = baseTotal.reset_index(drop=True)
filasEliminar = []
baseTotal = Merge(baseTotal, amortizacion)
baseTotal = OrdenarValores(baseTotal)
#baseTotal = EliminarFilasSobrantes(baseTotal, filasEliminar)

baseTotal = baseTotal.drop(['IdPrestamo', 'Cuota','Concepto','Debito'], axis=1)

print ("Creando archivo")
CrearExcel("C:/Users/Jhon Camargo/OneDrive - Deltacredit S.A.S/DBA/Automatizaciones/ReporteSaldos/Salidas/ReporteSaldosPruebaDos.xlsx", "BaseTotal", baseTotal, False)
print ("Termino")

                    