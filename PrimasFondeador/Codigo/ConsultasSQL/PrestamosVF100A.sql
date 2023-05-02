SELECT 
PD.Descripcion AS 'DescripcionCredito',
PD.FechaInicial, 
PD.CapitalInicial, 
PD.Plazo, 
PD.Ctivo, 
PD.Interes, 
PD.IdPrestamo, 
PD.ValorCuotaCorriente,
P.Descripcion AS 'DescripcionVenta',
P.FechaInicial AS 'FechaInicialVenta', 
P.FechaDesembolso AS 'FechaDesembolsoVenta',
P.CapitalInicial AS 'CapitalInicialVenta', 
P.Plazo AS 'PlazoVenta', 
P.Ctivo AS 'CtivoVenta', 
P.Interes AS 'InteresVenta', 
P.IdPrestamo AS 'IdPrestamoVenta', 
P.ValorCuotaCorriente AS 'ValorCuotaCorrienteVenta'
FROM prstms P
INNER JOIN valorescapturasdinamicas V ON P.solicitud = V.NoProducto
INNER JOIN prstms PD ON V.Valor = PD.Ctivo
INNER JOIN valorescapturasdinamicas VM ON P.solicitud = VM.NoProducto AND VM.Valor = 'VF100A'
WHERE P.idestado = 'ACTIVO'  AND V.IdCaptura = 'TXT_CTIVOCLI'
ORDER BY V.Valor


