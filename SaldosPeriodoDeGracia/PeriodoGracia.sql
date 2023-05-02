SELECT
p.Ctivo AS 'Credito',
p.IdEstado AS 'Estado',
p.Plazo AS 'Plazo',
CASE WHEN PS.SCActual>0 THEN PS.Cpagadas-1 ELSE PS.CPagadas END AS 'CuotasPagadas', 
ISNULL(pg.ValorGracia,0) AS 'CXC Periodo De Gracia',
ISNULL(pg.ValorGracia,0) * CASE WHEN PS.SCActual>0 THEN PS.Cpagadas-1 ELSE PS.CPagadas END AS 'Periodo Gracia Pagado',
ISNULL(pg.ValorGracia,0) * p.plazo AS 'Saldo Perido Gracia',
(ISNULL(pg.ValorGracia,0) * p.plazo) - (ISNULL(pg.ValorGracia,0) * CASE WHEN PS.SCActual>0 THEN PS.Cpagadas-1 ELSE PS.CPagadas END) AS ' Saldo Total Pendiente '
FROM prstms p
INNER JOIN prstmssaldos ps ON p.idPrestamo = ps.idPrestamo
LEFT JOIN (select idPrestamo, valor AS 'ValorGracia' from prestamoscargos where tipoCargo = 'CUOTA' and nombre = 'PGRACIA') pg ON p.idPrestamo = pg.idPrestamo
WHERE p.IdTipoPrestamo = 'PFIJA'

select *
from prstms
where idprestamo = '1211'

select *
from prstmssaldos
where idprestamo in ('1149','1209','1211','1205')

select *
from conceptosxfondo
where idprestamo in ('1209','1211')
