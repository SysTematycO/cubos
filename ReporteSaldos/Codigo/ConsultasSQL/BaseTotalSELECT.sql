IF OBJECT_ID('tempdb..#ContaDetalleCausacionBaseTotal') IS NOT NULL  
   BEGIN  
    DROP TABLE #ContaDetalleCausacionBaseTotal;
END
CREATE TABLE #ContaDetalleCausacionBaseTotal (
FechaEfectiva VARCHAR(50) COLLATE Modern_Spanish_CI_AS 
,CREDITO VARCHAR(50) COLLATE Modern_Spanish_CI_AS 
,Valor VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Debito VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Concepto VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
)
INSERT INTO #ContaDetalleCausacionBaseTotal
SELECT SUBSTRING(CONVERT(varchar, d.fechaEfectiva ,21),0,LEN(d.fechaEfectiva)-8) AS 'FechaEfectiva', p.Ctivo, c.Valor, c.Debito, c.Memo
FROM contadetalle c
INNER JOIN Diario d ON c.idDiario = d.idDiario AND d.idTrx <> '0645'
INNER JOIN (SELECT * FROM prstms WHERE idTipoPrestamo = 'PFIJA') p ON c.IdPrestamo = p.IdPrestamo
WHERE (c.memo = 'CXC INTERES CORRIENTE' or c.memo = 'CXC SEGURO' or c.memo = 'INTERESES POR DIFERIR PERIODO DE GRACIA' or c.memo = 'BUSURA') and c.debito != 0
ORDER BY p.Ctivo, d.fechaEfectiva


IF OBJECT_ID('tempdb..#AmortizacionVariableCausacionBaseTotal') IS NOT NULL  
   BEGIN  
    DROP TABLE #AmortizacionVariableCausacionBaseTotal;
END
CREATE TABLE #AmortizacionVariableCausacionBaseTotal (
FechaEfectiva VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,CREDITO VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,Concepto VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Debito VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
)
INSERT INTO #AmortizacionVariableCausacionBaseTotal
SELECT CAST (a.fechavencimiento AS VARCHAR) AS 'FechaEfectiva', p.Ctivo, a.Concepto, a.Valor AS 'Debito'
FROM amortizacionvariable a
INNER JOIN (SELECT * FROM prstms WHERE idTipoPrestamo = 'PFIJA') p ON a.IdPrestamo = p.IdPrestamo
ORDER BY p.ctivo, a.fechavencimiento


SELECT tf.*, 
ISNULL(cdi.Debito,0) AS 'CXC INTERES CORRIENTE', 
ISNULL(cds.Debito,0) AS 'CXC SEGURO',
ISNULL(cdg.Debito,0) AS 'INTERESES POR DIFERIR PERIODO DE GRACIA',
ISNULL(cdb.Debito,0) AS 'BUSURA',
ISNULL(avgac.Debito,0) AS 'GAC',
ISNULL(avm.Debito,0) AS 'IMORA',
ISNULL(avig.Debito,0) AS 'IVAGAC'
FROM TABLAAMORTIZACIONFONDEADOR tf
LEFT JOIN (SELECT DISTINCT * FROM #ContaDetalleCausacionBaseTotal) cdi ON cdi.CREDITO = tf.CREDITO AND cdi.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND cdi.Concepto = 'CXC INTERES CORRIENTE'
LEFT JOIN (SELECT DISTINCT * FROM #ContaDetalleCausacionBaseTotal) cds ON cds.CREDITO = tf.CREDITO AND cds.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND cds.Concepto = 'CXC SEGURO'
LEFT JOIN (SELECT DISTINCT * FROM #ContaDetalleCausacionBaseTotal) cdg ON cdg.CREDITO = tf.CREDITO AND cdg.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND cdg.Concepto = 'INTERESES POR DIFERIR PERIODO DE GRACIA'
LEFT JOIN (SELECT DISTINCT * FROM #ContaDetalleCausacionBaseTotal) cdb ON cdb.CREDITO = tf.CREDITO AND cdb.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND cdb.Concepto = 'BUSURA'
LEFT JOIN (SELECT DISTINCT * FROM #AmortizacionVariableCausacionBaseTotal) avgac ON avgac.CREDITO = tf.CREDITO AND avgac.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND avgac.Concepto = 'GAC'
LEFT JOIN (SELECT DISTINCT * FROM #AmortizacionVariableCausacionBaseTotal) avm ON avm.CREDITO = tf.CREDITO AND avm.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND avm.Concepto = 'IMORA'
LEFT JOIN (SELECT DISTINCT * FROM #AmortizacionVariableCausacionBaseTotal) avig ON avig.CREDITO = tf.CREDITO AND avig.FechaEfectiva = tf.FECHAVENCIMIENTOAMORTIZACION AND avig.Concepto = 'IVAGAC'
ORDER BY tf.CREDITO, tf.FECHAVENCIMIENTOAMORTIZACION
