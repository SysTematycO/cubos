USE K003_2
SELECT *,
    CASE 
    WHEN t.CUENTA_RECAUDO='BANCO DE OCCIDENTE AHORROS 263857963' OR  t.CUENTA_RECAUDO='BANCO IRIS BANK' THEN 'BANCO DELTA' 
    WHEN t.CUENTA_RECAUDO='BANCO DENK S.A.S' OR  t.CUENTA_RECAUDO='BANCO INVERSIONES BALERNO' OR 
    t.CUENTA_RECAUDO='BANCO INVERSIONES POU' OR  t.CUENTA_RECAUDO='BANCO JULIANA SGUERRA' OR 
    t.CUENTA_RECAUDO='BANCO RENTEK' OR  t.CUENTA_RECAUDO='P.A.C.E. CONSULTING S.A.S'THEN 'BANCO FONDEADORES'
    WHEN t.CUENTA_RECAUDO='ACUERDOS EN CURSO' OR  t.CUENTA_RECAUDO='AJUSTE' OR
    t.CUENTA_RECAUDO='AJUSTE NIVELACION' OR  t.CUENTA_RECAUDO='APLICACION SALDOS' OR
    t.CUENTA_RECAUDO='CASTIGOS DE CARTERA' OR  t.CUENTA_RECAUDO='CREDITO EN CURSO' OR
    t.CUENTA_RECAUDO='PAGO EN CURSO' OR  t.CUENTA_RECAUDO='PARTIDAS CONCILIATORIAS'THEN 'NO BANCARIOS'
    END
    AS 'CATEGORIA',
	FORMAT(t.FECHA_APLICACION,'yyyy-MM') AS	MESA�O

FROM DistribucionDePagos t