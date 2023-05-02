IF OBJECT_ID('tempdb..AmortizacionVariableCausacionBaseTotal') IS NOT NULL  
   BEGIN  
    DROP TABLE AmortizacionVariableCausacionBaseTotal;
END
CREATE TABLE AmortizacionVariableCausacionBaseTotal (
FechaEfectiva VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,CREDITO VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,IdPrestamo VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Cuota VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Concepto VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Debito VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
)
INSERT INTO AmortizacionVariableCausacionBaseTotal
SELECT CAST (a.fechavencimiento AS VARCHAR) AS 'FechaEfectiva', p.Ctivo ,a.IdPrestamo, a.Cuota, a.Concepto, a.Valor AS 'Debito'
FROM amortizacionvariable a
INNER JOIN (SELECT * FROM prstms WHERE idTipoPrestamo = 'PFIJA') p ON a.IdPrestamo = p.IdPrestamo
ORDER BY idprestamo, fechavencimiento
