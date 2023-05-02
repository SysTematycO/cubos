IF OBJECT_ID('tempdb..ContaDetalleCausacionBaseTotal') IS NOT NULL  
   BEGIN  
    DROP TABLE ContaDetalleCausacionBaseTotal;
END
CREATE TABLE ContaDetalleCausacionBaseTotal (
FechaEfectiva VARCHAR(50) COLLATE Modern_Spanish_CI_AS 
,CREDITO VARCHAR(50) COLLATE Modern_Spanish_CI_AS 
,IdDiario VARCHAR(50) COLLATE Modern_Spanish_CI_AS 
,IdPrestamo VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Valor VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Debito VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
,Concepto VARCHAR(50)  COLLATE Modern_Spanish_CI_AS
)
INSERT INTO ContaDetalleCausacionBaseTotal
SELECT SUBSTRING(CONVERT(varchar, d.fechaEfectiva ,21),0,LEN(d.fechaEfectiva)-8) AS 'FechaEfectiva', p.Ctivo ,c.IdDiario, c.IdPrestamo, c.Valor, c.Debito, c.Memo
FROM contadetalle c
INNER JOIN Diario d ON c.idDiario = d.idDiario
INNER JOIN (SELECT * FROM prstms WHERE idTipoPrestamo = 'PFIJA') p ON c.IdPrestamo = p.IdPrestamo
WHERE (c.memo = 'CXC INTERES CORRIENTE' or c.memo = 'CXC SEGURO' or c.memo = 'INTERESES POR DIFERIR PERIODO DE GRACIA' or c.memo = 'BUSURA') and c.debito != 0
ORDER BY p.Ctivo, d.fechaEfectiva
