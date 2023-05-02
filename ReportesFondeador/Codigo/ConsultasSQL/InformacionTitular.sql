SELECT 
prs.Ctivo AS 'Credito'
,pd.Direccion AS 'Direccion'
,pd.Barrio AS 'Barrio'
,cd.CIUDAD AS 'Ciudad'
,cd.DEPARTAMENTO AS 'Departamento'
FROM Personas p
INNER JOIN (SELECT * FROM Prstms WHERE idTipoPrestamo = 'PFIJA' AND idEstado = 'ACTIVO') prs ON p.Ndoc = prs.Ndoc
LEFT JOIN (SELECT NDoc, MIN(Linea1) AS 'Direccion', MIN(Barrio) AS 'Barrio', MIN(Telefono) AS 'Telefono', MIN(CodDane) AS 'CodDane' 
FROM PDirecciones GROUP BY NDoc) pd ON p.NDoc = pd.NDoc
LEFT JOIN CODIGOSDANE cd ON pd.CodDane = cd.CODIGO