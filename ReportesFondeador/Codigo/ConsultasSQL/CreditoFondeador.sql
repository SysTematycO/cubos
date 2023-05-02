SELECT 
p.Ctivo AS 'NoCREDITO'
,p.Ndoc AS 'CEDULA'
,p.Producto AS 'PRODUCTO'
,pe.Nombres AS 'NOMBRE'
,pe.Email AS 'EMAIL'
,pe.Celular	AS 'CELULAR'
,p.CapitalInicial AS 'CAPITAL_INICIAL'
,p.Plazo AS 'PLAZO'
,p.Interes/100 AS 'TASA_CLIENTE'
,p.ValorCuotaTotal AS 'CUOTA_TOTAL'
,ps.SaldoCapital + ps.SCAK AS 'SALDO_CAPITAL'
,f.Nombre AS 'NOMBRE_FONDEADOR'
FROM Prstms p
INNER JOIN VentaXFondo v ON p.IdPrestamo = v.IdPrestamo
INNER JOIN Fondeador f ON v.NDocF = f.NDoc
INNER JOIN Prstms pd ON v.RefPrestamo = pd.IdPrestamo
INNER JOIN Personas pe ON p.NDoc = pe.NDoc
INNER JOIN PrstmsSaldos ps ON p.IdPrestamo = ps.IdPrestamo
WHERE p.IdTipoPrestamo = 'PFIJA' AND p.IdEstado = 'ACTIVO'
ORDER BY f.Nombre ASC

