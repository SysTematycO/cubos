DECLARE @IDKATIOS  CHAR(100) = 'DELTA',
	   @ESTADO VARCHAR(50) = 'TODOS',
	   @GENERAR VARCHAR(20)='SI',
	   @FECHAINICIAL date = '2019/01/01',
	   @FECHAFINAL VARCHAR(20) = '2022/11/02',
	   @CTIVOS VARCHAR(20)='0A'

IF @FECHAFINAL='GETDATE()'
BEGIN
	SET @FECHAFINAL=cast(FORMAT(GETDATE(),'yyyy/MM/dd') as varchar)
END 
DECLARE @IDPRESTAMOS VARCHAR(MAX);
SET @IDPRESTAMOS = CASE 
WHEN @CTIVOS='0A' 
THEN 
ISNULL((SELECT CAST(IDPRESTAMO AS VARCHAR) + ','FROM PRSTMS WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDESTADO<>'CREADO' AND PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos') for xml path('')),'')
ELSE 
ISNULL((SELECT CAST(IDPRESTAMO AS VARCHAR) + ','FROM PRSTMS WHERE IDKATIOS=@IDKATIOS AND PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos') AND CTIVO IN (SELECT VALUE FROM SPLIT (',',@CTIVOS))for xml path('')),'')
END
--VARIABLES CURSOR2
BEGIN
DECLARE @BDIDPRESTAMO NUMERIC(18,0);
DECLARE @BDCUOTA INT;
DECLARE @BDKPAGADO NUMERIC(18,0);
DECLARE @BDIPAGADO NUMERIC(18,0);
DECLARE @BDKPAGADOIMP NUMERIC(18,0);
DECLARE @BDIPAGADOIMP NUMERIC(18,0);
DECLARE @BDSALDOCAPITAL NUMERIC(18,0);
DECLARE @BDFECHAVENCIMIENTO DATE;
DECLARE @BDNUEVOFONDEADOR VARCHAR(50);
DECLARE @BDFONDEADOR VARCHAR(50)='';
DECLARE @BDVPNCORRIENTE NUMERIC(18,0);
DECLARE @BDVPN NUMERIC(18,0);
DECLARE @BDFECHAVENTA DATE;
DECLARE @BDFPPAGO DATE;
DECLARE @BDTASAVENTA NUMERIC(18,8);
DECLARE @BDCUOTAVENTA NUMERIC(18,0);
DECLARE @BDVALORVENTA NUMERIC(18,0);
DECLARE @BDbCUOTATOTAL VARCHAR(50);
DECLARE @BDSALDOFONDEADOR NUMERIC(18,0);
DECLARE @BDCUOTACTE NUMERIC(18,0);
DECLARE @BDCUOTATOTAL NUMERIC(18,0);
DECLARE @BDTIPOF VARCHAR(10);
DECLARE @BDCAPITALFON NUMERIC(18,0)
DECLARE @BDINTFONDEADORFON NUMERIC(18,0)
DECLARE @BDPLAZO INT;
DECLARE @BDCPAGADAS INT;
DECLARE @BDFECHAINICIAL DATE;
DECLARE @BDTASACLI NUMERIC(18,16);
DECLARE @BDTAMORTIZACION NUMERIC(18,2) = 1000;
DECLARE @BDESTADOCUO VARCHAR(100);
DECLARE @BDVPNTOTAL NUMERIC(18,2);

END
--CREAR TABLAS TEMPORALES
BEGIN

IF OBJECT_ID('tempdb..#DESEMBOLSOS') IS NOT NULL  
   BEGIN  
    DROP TABLE #DESEMBOLSOS;
END

IF OBJECT_ID('tempdb..#KPAGADO') IS NOT NULL  
   BEGIN  
    DROP TABLE #KPAGADO;
END

IF OBJECT_ID('tempdb..#IPAGADO') IS NOT NULL  
   BEGIN  
    DROP TABLE #IPAGADO;
END

IF OBJECT_ID('tempdb..#AMORTIZACIONCREDITO') IS NOT NULL  
   BEGIN  
    DROP TABLE #AMORTIZACIONCREDITO;
END

IF OBJECT_ID('tempdb..#CCARGOSADMIN') IS NOT NULL  
   BEGIN  
    DROP TABLE #CCARGOSADMIN;
END

IF OBJECT_ID('tempdb..#CCARGOSCUOTA') IS NOT NULL  
   BEGIN  
    DROP TABLE #CCARGOSCUOTA;
END

IF OBJECT_ID('tempdb..#GETFONDEADOR') IS NOT NULL  
   BEGIN  
    DROP TABLE #GETFONDEADOR;
END


CREATE TABLE #AMORTIZACIONCREDITO (
IDKATIOS VARCHAR(20) COLLATE Modern_Spanish_CI_AS 
,IDPRESTAMO VARCHAR(30) COLLATE Modern_Spanish_CI_AS 
,CUOTA NUMERIC(18,0)
,CAPITAL NUMERIC(18,0)
,INTERES NUMERIC(18,0)
,SALDOCAPITAL NUMERIC(18,0)
,FECHAVENCIMIENTO DATE
,VENTA VARCHAR(30) COLLATE Modern_Spanish_CI_AS 
,VALORNEGOCIADOTOTAL NUMERIC(18,0)
,VALORNEGOCIADOCORRIENTE NUMERIC(18,0)
,VPN NUMERIC(18,0)
,CAPITALFON NUMERIC(18,0)
,TIPOF VARCHAR(10)
,INTERESFON NUMERIC(18,0)
,SALDOFONDEADOR NUMERIC(18,0)
,ESTADOCUOTA VARCHAR(50)
,MORA NUMERIC(18,0)
,GASTOS_DE_COBRANZA NUMERIC(18,0)
,IVAGAC NUMERIC(18,0)
)

CREATE TABLE #CCARGOSADMIN (
IDKATIOS VARCHAR(20) COLLATE Modern_Spanish_CI_AS 
,IDPRESTAMO VARCHAR(20) COLLATE Modern_Spanish_CI_AS 
,VALOR NUMERIC(18,0)
)

CREATE TABLE #CCARGOSCUOTA (
IDKATIOS VARCHAR(20) COLLATE Modern_Spanish_CI_AS 
,IDPRESTAMO VARCHAR(20) COLLATE Modern_Spanish_CI_AS 
,VALOR NUMERIC(18,0)
)

CREATE TABLE #DESEMBOLSOS(
IdKatios VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,IdPrestamo VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,IdDiario VARCHAR(50) COLLATE Modern_Spanish_CI_AS
)

CREATE TABLE #KPAGADO(
IdKatios VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,IdPrestamo VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,Cuota INT
,Valor NUMERIC(18,2)
)

CREATE TABLE #IPAGADO(
IdKatios VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,IdPrestamo VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,Cuota INT
,Valor NUMERIC(18,2)
)

CREATE TABLE #GETFONDEADOR
(IDKATIOS VARCHAR(20) COLLATE Modern_Spanish_CI_AS
,IDPRESTAMO VARCHAR(20) COLLATE Modern_Spanish_CI_AS
,PROYECTO VARCHAR(20) COLLATE Modern_Spanish_CI_AS
,NOMBRE VARCHAR(300) COLLATE Modern_Spanish_CI_AS
,NDOC VARCHAR(50) COLLATE Modern_Spanish_CI_AS
,METODOLOGIA VARCHAR(50) COLLATE Modern_Spanish_CI_AS
)


END

IF @GENERAR='SI'
BEGIN

INSERT INTO #DESEMBOLSOS
SELECT
PRE.IdKatios
,PRE.IdPrestamo
,MAX(DRO.IdDiario)
FROM Prstms PRE WITH(NOLOCK)
INNER JOIN PRSTMSENC PE WITH(NOLOCK) ON PRE.IdKatios=PE.Idkatios AND PRE.IdPrestamo=PE.IdProducto AND PE.IdTrx='5007' AND PE.REFERENCIA NOT LIKE 'RV%'
INNER JOIN Diario DRO WITH(NOLOCK) ON PRE.IdKatios=DRO.IdKatios AND PE.IdDiario=DRO.IdDiario AND DRO.TIPOTRX<>'RV'
WHERE PRE.IDKATIOS=@IDKATIOS 
AND PRE.FECHADESEMBOLSO BETWEEN @FECHAINICIAL AND @FECHAFINAL 
AND (CASE WHEN @ESTADO='TODOS' THEN @ESTADO ELSE LTRIM(RTRIM(PRE.IDESTADO)) END) = LTRIM(RTRIM(@ESTADO))
AND PRE.IdPrestamo IN (SELECT VALUE FROM SPLIT (',',@IDPRESTAMOS)) 
GROUP BY PRE.IdKatios,PRE.IdPrestamo

INSERT INTO #KPAGADO
SELECT
PRE.IdKatios
,PC.IdPrestamo
,PE.CUOTA
,DATEDIFF(MONTH,PC.FechaInicial,VXF.FPPago)-1+SUM(PD.Debito-PD.Credito)
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN VentaXFondo VXF WITH(NOLOCK) ON PRE.IdKatios=VXF.IdKatios AND PRE.IdPrestamo=VXF.RefPrestamo
INNER JOIN Prstms PC WITH(NOLOCK) ON PRE.IdKatios=PC.IdKatios AND VXF.IdPrestamo=PC.IdPrestamo
INNER JOIN #DESEMBOLSOS DS WITH(NOLOCK) ON PRE.IdKatios=DS.IdKatios AND VXF.IdPrestamo=DS.IdPrestamo
INNER JOIN PRSTMSENC PE WITH(NOLOCK) ON PRE.IdKatios=PE.Idkatios AND PRE.IdPrestamo=PE.IdProducto
INNER JOIN PrstmsDetalle PD WITH(NOLOCK) ON PRE.IdKatios=PD.Idkatios AND PRE.IdPrestamo=PD.IdPrestamo AND PE.IdEncabezado=PD.IdEncabezado AND PE.IdDiario=PD.IdDiario AND PD.NombreCuenta='KPAGADO'
WHERE PRE.IdKatios=@IDKATIOS 
GROUP BY PRE.IdKatios,PC.IdPrestamo,PE.CUOTA,PC.FechaInicial,VXF.FPPago
ORDER BY PE.CUOTA

INSERT INTO #IPAGADO
SELECT
PRE.IdKatios
,PC.IdPrestamo
,PE.CUOTA
,DATEDIFF(MONTH,PC.FechaInicial,VXF.FPPago)-1+SUM(PD.Debito-PD.Credito)
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN VentaXFondo VXF WITH(NOLOCK) ON PRE.IdKatios=VXF.IdKatios AND PRE.IdPrestamo=VXF.RefPrestamo
INNER JOIN Prstms PC WITH(NOLOCK) ON PRE.IdKatios=PC.IdKatios AND VXF.IdPrestamo=PC.IdPrestamo
INNER JOIN #DESEMBOLSOS DS WITH(NOLOCK) ON PRE.IdKatios=DS.IdKatios AND VXF.IdPrestamo=DS.IdPrestamo
INNER JOIN PRSTMSENC PE WITH(NOLOCK) ON PRE.IdKatios=PE.Idkatios AND PRE.IdPrestamo=PE.IdProducto
INNER JOIN PrstmsDetalle PD WITH(NOLOCK) ON PRE.IdKatios=PD.Idkatios AND PRE.IdPrestamo=PD.IdPrestamo AND PE.IdEncabezado=PD.IdEncabezado AND PE.IdDiario=PD.IdDiario AND PD.NombreCuenta='IPAGADO'
WHERE PRE.IdKatios=@IDKATIOS 
GROUP BY PRE.IdKatios,PC.IdPrestamo,PE.CUOTA,PC.FechaInicial,VXF.FPPago
ORDER BY PE.CUOTA

INSERT INTO #GETFONDEADOR
SELECT 
FON.IdKatios
,VXF.IdPrestamo
,VXF.Proyecto
,FON.Nombre
,PV.NDocForndedador
,VXF.Metodologia
FROM Prstms PRE
LEFT JOIN VentaXFondo VXF WITH(NOLOCK) ON PRE.IdKatios=VXF.IdKatios AND PRE.IdPrestamo=VXF.IdPrestamo AND VXF.Estado='ACTIVO'
LEFT JOIN Prstms PV WITH(NOLOCK) ON PRE.IdKatios=PV.IdKatios AND VXF.RefPrestamo=PV.IdPrestamo
LEFT JOIN Fondeador FON WITH(NOLOCK) ON PRE.IdKatios=FON.IdKatios AND PV.TDocFondeador=FON.TDoc AND PV.NDocForndedador=FON.NDoc
WHERE VXF.IdKatios=@IDKATIOS AND VXF.Estado='ACTIVO'

DELETE TABLAAMORTIZACIONFONDEADOR
--CURSOR PARA CUOTAS PAGADAS
BEGIN
DECLARE AMORTIZACION_BD CURSOR FOR 
SELECT
PRE.IdPrestamo
,PS.Cpagadas
,ISNULL(PRE.SaldoInicial,PRE.CAPITALINICIAL)
,PS.SCAK
,PS.SCAI
,PRE.ValorCuotaCorriente
,PRE.ValorCuotaTotal
,PRE.Plazo
,PRE.FechaInicial
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN #DESEMBOLSOS DS WITH(NOLOCK) ON PRE.IdKatios=DS.IdKatios AND PRE.IdPrestamo=DS.IdPrestamo
INNER JOIN PrstmsSaldos PS WITH(NOLOCK) ON PRE.IdKatios=PS.IdKatios AND PRE.IdPrestamo=PS.IdPrestamo
WHERE PRE.IdKatios=@IDKATIOS
--AND (ISNULL(KPG.Valor,0)+ISNULL(IPG.Valor,0))<>0
OPEN AMORTIZACION_BD
FETCH NEXT FROM AMORTIZACION_BD INTO @BDIDPRESTAMO,@BDCPAGADAS,@BDSALDOCAPITAL,@BDKPAGADO,@BDIPAGADO,@BDCUOTACTE,@BDCUOTATOTAL,@BDPLAZO,@BDFECHAINICIAL
WHILE @@fetch_status = 0
	BEGIN
		SET @BDCUOTA= 1;
		set @BDKPAGADOIMP= 0;
		set @BDIPAGADOIMP= 0;
	
		WHILE @BDCUOTA <= @BDCPAGADAS
		BEGIN
		
			SET @BDFECHAVENCIMIENTO= DATEADD(MONTH,@BDCUOTA,@BDFECHAINICIAL)
			IF @BDCUOTA=@BDCPAGADAS AND (@BDKPAGADO + @BDIPAGADO)>0
			BEGIN
			SET @BDKPAGADOIMP= @BDKPAGADO;
			SET @BDIPAGADOIMP= @BDIPAGADO;
			SET @BDESTADOCUO='PARCIAL'
			END
			ELSE
			BEGIN
			SET @BDKPAGADOIMP= 0;
			SET @BDIPAGADOIMP= 0;
			SET @BDESTADOCUO='PAGADA'
			END

			SET @BDCAPITALFON=0
			SET @BDSALDOFONDEADOR=0
			SET @BDINTFONDEADORFON=0
			SET @BDFONDEADOR=''
			SET @BDNUEVOFONDEADOR=''
			SET @BDTASAVENTA=0
			SET @BDVPNCORRIENTE=0
			SET @BDVPNTOTAL=0
			SET @BDVPN=0
			SET @BDCUOTAVENTA=0
			SET @BDVALORVENTA=0
			SET @BDSALDOFONDEADOR=0
			SET @BDTIPOF=0
			SET @BDbCUOTATOTAL=0
			SET @BDNUEVOFONDEADOR=0
			SET @BDCAPITALFON=0
			SET @BDINTFONDEADORFON =0	

			SET @BDNUEVOFONDEADOR=ISNULL((SELECT TOP 1 VXF.PROYECTO FROM VENTAXFONDO VXF WITH(NOLOCK) INNER JOIN VENTADETALLE VD WITH(NOLOCK) ON VXF.IDKATIOS=VD.IDKATIOS AND VXF.IdPrestamo=VD.IdPrestamo AND VXF.Proyecto=VD.Proyecto AND VD.Cuota=@BDCUOTA WHERE VXF.IDKATIOS=@IDKATIOS AND VXF.IDPRESTAMO=@BDIDPRESTAMO AND VXF.FPPAGO <=@BDFECHAVENCIMIENTO AND (VXF.Estado='ACTIVO' OR VXF.FUPAGO>=@BDFECHAVENCIMIENTO ) ORDER BY VXF.FCOMPRA DESC),'') 
		
			IF @BDNUEVOFONDEADOR<>''
				SET @BDFONDEADOR =@BDNUEVOFONDEADOR
				SET @BDFECHAVENTA = (SELECT FCOMPRA FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDTASAVENTA= ISNULL((SELECT ISNULL(TASA,0) FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR),0)
				SET @BDFPPAGO= (SELECT FPPAGO FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDVALORVENTA= (SELECT VALORNEGOCIACION FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDCUOTAVENTA=(SELECT CVENDIDAS FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDbCUOTATOTAL=(SELECT CUOTAtotal FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDSALDOFONDEADOR=@BDVALORVENTA
				SET @BDTIPOF  =(SELECT ISNULL(TIPOF,'P') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	
				IF @BDCUOTA>= DATEDIFF(MONTH,@BDFECHAINICIAL,@BDFPPAGO) AND @BDCUOTA<= DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO))
				BEGIN			
					IF @BDbCUOTATOTAL='TRUE' 
					BEGIN
						SET @BDCAPITALFON=CASE WHEN @BDVALORVENTA=-1 THEN 0 ELSE dbo.PPMT((POWER(CAST((1.000000+@BDTASAVENTA) AS float),(1.000000/12.000000)) -1), @BDCUOTA,DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO)), - @BDVALORVENTA , 0, 0) END
						SET @BDINTFONDEADORFON =@BDCUOTATOTAL -@BDCAPITALFON
						--SET @BDVPNTOTAL=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTATOTAL,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDVPNTOTAL = (SELECT ISNULL(ValorNegociacion,'0') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	 
						SET @BDVPNCORRIENTE=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDVPN=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTATOTAL,@BDTASAVENTA * 100,datediff(d,@FECHAFINAL,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDSALDOFONDEADOR=@BDSALDOFONDEADOR-@BDCAPITALFON
						SET @BDSALDOCAPITAL= @BDSALDOCAPITAL- @BDKPAGADO
					END
					ELSE
					BEGIN
						SET @BDCAPITALFON=CASE WHEN @BDVALORVENTA=-1 THEN 0 ELSE dbo.PPMT((POWER(CAST((1.000000+@BDTASAVENTA) AS float),(1.000000/12.000000)) -1), @BDCUOTA,DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO)), - @BDVALORVENTA , 0, 0) END
						SET @BDINTFONDEADORFON =@BDCUOTACTE -@BDCAPITALFON
						--SET @BDVPNTOTAL=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDVPNTOTAL = (SELECT ISNULL(ValorNegociacion,'0') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	 
						SET @BDVPNCORRIENTE=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDVPN=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@FECHAFINAL,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDSALDOFONDEADOR=@BDSALDOFONDEADOR-@BDCAPITALFON
						SET @BDSALDOCAPITAL= @BDSALDOCAPITAL- @BDKPAGADO
					END
				END
				ELSE
					BEGIN
					SET @BDFONDEADOR ='';
				END
			
			INSERT INTO #AMORTIZACIONCREDITO 
			(IDKATIOS,IDPRESTAMO,CUOTA,CAPITAL,INTERES,SALDOCAPITAL,FECHAVENCIMIENTO,VENTA,VALORNEGOCIADOCORRIENTE,VALORNEGOCIADOTOTAL,VPN,CAPITALFON,TIPOF,INTERESFON,SALDOFONDEADOR,ESTADOCUOTA,MORA,GASTOS_DE_COBRANZA,IVAGAC)
			VALUES
			(@IDKATIOS,@BDIDPRESTAMO,@BDCUOTA,@BDKPAGADOIMP,@BDIPAGADOIMP,@BDSALDOCAPITAL,@BDFECHAVENCIMIENTO,ISNULL(@BDFONDEADOR,''),ISNULL(@BDVPNCORRIENTE,0),ISNULL(@BDVPNTOTAL,0),ISNULL(@BDVPN,0),ISNULL(@BDCAPITALFON,0),ISNULL(@BDTIPOF,''),ISNULL(@BDINTFONDEADORFON,0),ISNULL(@BDSALDOFONDEADOR,0),@BDESTADOCUO,0,0,0)

			SET @BDCUOTA= @BDCUOTA + 1;
			
			END
		FETCH NEXT FROM AMORTIZACION_BD INTO @BDIDPRESTAMO,@BDCPAGADAS,@BDSALDOCAPITAL,@BDKPAGADO,@BDIPAGADO,@BDCUOTACTE,@BDCUOTATOTAL,@BDPLAZO,@BDFECHAINICIAL
	END
CLOSE AMORTIZACION_BD
DEALLOCATE AMORTIZACION_BD
END

-- CURSOR PARA RECORRER CREDITOS E INSERTAR REGISTROS EN #AMORTIZACIONCREDITO
BEGIN
	PRINT('COMIENZO AMORTIZACION_CLIENTE')
	DECLARE AMORTIZACION_CLIENTE CURSOR FOR 
	SELECT 
	PRE.IdPrestamo
	,PS.Cpagadas
	,PS.SaldoCapital
	,PRE.ValorCuotaCorriente
	,PRE.ValorCuotaTotal
	,PRE.FechaInicial
	,PRE.Interes
	,PRE.PLAZO
	FROM PRSTMS PRE WITH(NOLOCK)
	INNER JOIN #DESEMBOLSOS DS WITH(NOLOCK) ON PRE.IdKatios=DS.IdKatios AND PRE.IdPrestamo=DS.IdPrestamo
	INNER JOIN PrstmsSaldos PS WITH(NOLOCK) ON PRE.IdKatios=PS.IdKatios AND PRE.IdPrestamo=PS.IdPrestamo
	WHERE PRE.IDKATIOS=@IDKATIOS  AND PS.SALDOCAPITAL<>0 AND PRE.IDESTADO<>'0'
	OPEN AMORTIZACION_CLIENTE  
	FETCH NEXT FROM AMORTIZACION_CLIENTE INTO @BDIDPRESTAMO,@BDCUOTA,@BDSALDOCAPITAL,@BDCUOTACTE,@BDCUOTATOTAL,@BDFECHAINICIAL,@BDTASACLI,@BDPLAZO
	WHILE @@fetch_status = 0
	BEGIN
		SET @BDCAPITALFON=0
		SET @BDSALDOFONDEADOR=0
		SET @BDINTFONDEADORFON=0
		SET @BDFONDEADOR=''
		SET @BDNUEVOFONDEADOR=''
		SET @BDTASAVENTA=0
		SET @BDVPNCORRIENTE=0
		SET @BDVPN=0
		SET @BDVPNCORRIENTE=0
			SET @BDVPNTOTAL=0
		SET @BDCUOTAVENTA=0
		SET @BDVALORVENTA=0
		SET @BDSALDOFONDEADOR=0
		SET @BDTIPOF=0
		SET @BDbCUOTATOTAL=0
		SET @BDNUEVOFONDEADOR=0
		SET @BDCAPITALFON=0
		SET @BDINTFONDEADORFON =0
		PRINT(@BDIDPRESTAMO)
		PRINT(@BDSALDOCAPITAL)
		PRINT(@BDTAMORTIZACION)
		PRINT(@BDCUOTA)
		PRINT(@BDPLAZO)
		WHILE @BDSALDOCAPITAL > @BDTAMORTIZACION OR @BDCUOTA < @BDPLAZO
		
		BEGIN 
			PRINT(@BDCUOTA)
			PRINT(@BDSALDOCAPITAL)
			PRINT(@BDTAMORTIZACION)
			IF @BDSALDOCAPITAL > 0
			BEGIN
			IF @BDSALDOCAPITAL > @BDTAMORTIZACION
			BEGIN
			IF @BDSALDOCAPITAL < @BDTAMORTIZACION
			BEGIN
				SET @BDIPAGADO=@BDSALDOCAPITAL*(@BDTASACLI/100)
				SET @BDKPAGADO=@BDSALDOCAPITAL
				SET @BDSALDOCAPITAL=0
				SET @BDCUOTA=@BDCUOTA+1
			END
			ELSE
			BEGIN
				SET @BDIPAGADO=@BDSALDOCAPITAL*(@BDTASACLI/100)
				SET @BDKPAGADO=@BDCUOTACTE-@BDIPAGADO
				IF @BDKPAGADO > @BDSALDOCAPITAL
				BEGIN
				SET @BDKPAGADO=@BDSALDOCAPITAL
				SET @BDSALDOCAPITAL=0
				END
				
				SET @BDSALDOCAPITAL=@BDSALDOCAPITAL-@BDKPAGADO
				SET @BDCUOTA=@BDCUOTA+1
			END
			
			END
			ELSE
			BEGIN
			SET @BDIPAGADO= 0
			SET @BDKPAGADO= 0
			SET @BDCUOTA=@BDCUOTA+1
			END
			
			

			SET @BDFECHAVENCIMIENTO= DATEADD(MONTH,@BDCUOTA,@BDFECHAINICIAL)

			--CALCULOS VENTA
			SET @BDNUEVOFONDEADOR=ISNULL((SELECT TOP 1 VXF.PROYECTO FROM VENTAXFONDO VXF WITH(NOLOCK) INNER JOIN VENTADETALLE VD WITH(NOLOCK) ON VXF.IDKATIOS=VD.IDKATIOS AND VXF.IdPrestamo=VD.IdPrestamo AND VXF.Proyecto=VD.Proyecto AND VD.Cuota=@BDCUOTA WHERE VXF.IDKATIOS=@IDKATIOS AND VXF.IDPRESTAMO=@BDIDPRESTAMO AND VXF.FPPAGO <=@BDFECHAVENCIMIENTO AND (VXF.Estado='ACTIVO' OR VXF.FUPAGO>=@BDFECHAVENCIMIENTO ) ORDER BY VXF.FCOMPRA DESC),'') 
			IF @BDNUEVOFONDEADOR<>''
			BEGIN
				SET @BDFONDEADOR =@BDNUEVOFONDEADOR

				SET @BDFECHAVENTA = (SELECT FCOMPRA FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDTASAVENTA= ISNULL((SELECT ISNULL(TASA,0) FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR),0)
				SET @BDFPPAGO= (SELECT FPPAGO FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDVALORVENTA= (SELECT VALORNEGOCIACION FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDCUOTAVENTA=(SELECT CVENDIDAS FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDbCUOTATOTAL=(SELECT CUOTAtotal FROM VENTAXFONDO WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR)
				SET @BDSALDOFONDEADOR=@BDVALORVENTA
				SET @BDTIPOF  =(SELECT ISNULL(TIPOF,'P') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	
				IF @BDCUOTA>= DATEDIFF(MONTH,@BDFECHAINICIAL,@BDFPPAGO) AND @BDCUOTA<= DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO))
				BEGIN			
					IF @BDbCUOTATOTAL='TRUE' 
					BEGIN
						SET @BDCAPITALFON=CASE WHEN @BDVALORVENTA=-1 THEN 0 ELSE dbo.PPMT((POWER(CAST((1.000000+@BDTASAVENTA) AS float),(1.000000/12.000000)) -1), @BDCUOTA,DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO)), - @BDVALORVENTA , 0, 0) END
						SET @BDINTFONDEADORFON =@BDCUOTATOTAL -@BDCAPITALFON
						--SET @BDVPNTOTAL=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTATOTAL,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDVPNTOTAL = (SELECT ISNULL(ValorNegociacion,'0') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	 
						SET @BDVPNCORRIENTE=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDVPN=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTATOTAL,@BDTASAVENTA * 100,datediff(d,@FECHAFINAL,@BDFECHAVENCIMIENTO)/365.00000000),0),0)
						SET @BDSALDOFONDEADOR=@BDSALDOFONDEADOR-@BDCAPITALFON
					END
					ELSE
					BEGIN
						SET @BDCAPITALFON=CASE WHEN @BDVALORVENTA=-1 THEN 0 ELSE dbo.PPMT((POWER(CAST((1.000000+@BDTASAVENTA) AS float),(1.000000/12.000000)) -1), @BDCUOTA,DATEDIFF(MONTH,@BDFECHAINICIAL,DATEADD(MONTH,@BDCUOTAVENTA-1,@BDFPPAGO)), - @BDVALORVENTA , 0, 0) END
						SET @BDINTFONDEADORFON =@BDCUOTACTE -@BDCAPITALFON
						--SET @BDVPNTOTAL=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDVPNTOTAL = (SELECT ISNULL(ValorNegociacion,'0') FROM VENTADETALLE WITH(NOLOCK) WHERE IDKATIOS=@IDKATIOS AND IDPRESTAMO=@BDIDPRESTAMO AND PROYECTO=@BDFONDEADOR AND CUOTA=@BDCUOTA)	 
						SET @BDVPNCORRIENTE=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@BDFECHAVENTA,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDVPN=ISNULL(ROUND(dbo.fnPresentValue(@BDCUOTACTE,@BDTASAVENTA * 100,datediff(d,@FECHAFINAL,@BDFechavencimiento)/365.00000000),0),0)
						SET @BDSALDOFONDEADOR=@BDSALDOFONDEADOR-@BDCAPITALFON
					END
				END
				ELSE
				BEGIN
				SET @BDFONDEADOR ='';
			END
			END
			INSERT INTO #AMORTIZACIONCREDITO 
			(IDKATIOS,IDPRESTAMO,CUOTA,CAPITAL,INTERES,SALDOCAPITAL,FECHAVENCIMIENTO,VENTA,VALORNEGOCIADOCORRIENTE,VALORNEGOCIADOTOTAL,VPN,CAPITALFON,TIPOF,INTERESFON,SALDOFONDEADOR,ESTADOCUOTA,MORA,GASTOS_DE_COBRANZA,IVAGAC)
			VALUES
			(@IDKATIOS,@BDIDPRESTAMO,@BDCUOTA,@BDKPAGADO,@BDIPAGADO,@BDSALDOCAPITAL,@BDFECHAVENCIMIENTO,ISNULL(@BDFONDEADOR,''),ISNULL(@BDVPNCORRIENTE,0),ISNULL(@BDVPNTOTAL,0),ISNULL(@BDVPN,0),ISNULL(@BDCAPITALFON,0),ISNULL(@BDTIPOF,''),ISNULL(@BDINTFONDEADORFON,0),ISNULL(@BDSALDOFONDEADOR,0),(CASE WHEN @BDFECHAVENCIMIENTO<@FECHAFINAL THEN 'VENCIDA' WHEN (@BDKPAGADO + @BDIPAGADO) = 0 THEN 'PAGADA' ELSE 'PENDIENTE' END),0,0,0)

			END
			ELSE
			BEGIN 
				SET @BDCUOTA=@BDPLAZO
			END
			-- SIMULAR AMORTIZACION		
			
		END
		FETCH NEXT FROM AMORTIZACION_CLIENTE INTO @BDIDPRESTAMO,@BDCUOTA,@BDSALDOCAPITAL,@BDCUOTACTE,@BDCUOTATOTAL,@BDFECHAINICIAL,@BDTASACLI,@BDPLAZO
	END
	CLOSE AMORTIZACION_CLIENTE
	DEALLOCATE AMORTIZACION_CLIENTE
END
PRINT('TERMINO AMORTIZACION_CLIENTE')
-- INSERTA REGISTROS CON INFORMACION DEL VALOR DE LOS CARGOS ADMIN POR PRESTAMO
INSERT INTO	#CCARGOSADMIN
SELECT
PRE.IDKATIOS
,PRE.IDPRESTAMO
,SUM(PC.VALOR)
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN PRESTAMOSCARGOS PC WITH(NOLOCK) ON PRE.IDKATIOS=PC.IDKATIOS AND PRE.IDPRESTAMO=PC.IDPRESTAMO AND PC.FININCLUIDO='1' AND PC.TIPOCARGO='ADMIN'
WHERE PRE.IDKATIOS=@IDKATIOS 
AND PRE.FECHADESEMBOLSO BETWEEN @FECHAINICIAL AND @FECHAFINAL 
AND (CASE WHEN @ESTADO='TODOS' THEN @ESTADO ELSE LTRIM(RTRIM(PRE.IDESTADO)) END) = LTRIM(RTRIM(@ESTADO)) 
AND PRE.IdPrestamo IN (SELECT VALUE FROM SPLIT (',',@IDPRESTAMOS)) 
GROUP BY PRE.IDKATIOS,PRE.IDPRESTAMO
-- INSERTA REGISTROS CON INFORMACION DEL VALOR DE LOS CARGOS CUOTA POR PRESTAMO
INSERT INTO	#CCARGOSCUOTA
SELECT
PRE.IDKATIOS
,PRE.IDPRESTAMO
,SUM(PC.VALOR)
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN PRESTAMOSCARGOS PC WITH(NOLOCK) ON PRE.IDKATIOS=PC.IDKATIOS AND PRE.IDPRESTAMO=PC.IDPRESTAMO AND PC.FININCLUIDO='1' AND PC.TIPOCARGO='CUOTA'
WHERE PRE.IDKATIOS=@IDKATIOS 
AND PRE.FECHADESEMBOLSO BETWEEN @FECHAINICIAL AND @FECHAFINAL 
AND (CASE WHEN @ESTADO='TODOS' THEN @ESTADO ELSE LTRIM(RTRIM(PRE.IDESTADO)) END) = LTRIM(RTRIM(@ESTADO))
AND PRE.IdPrestamo IN (SELECT VALUE FROM SPLIT (',',@IDPRESTAMOS)) 
GROUP BY PRE.IDKATIOS,PRE.IDPRESTAMO

--INSERTA REGISTROS PARA CONSULTA FINAL
INSERT INTO TABLAAMORTIZACIONFONDEADOR
(
CREDITO
,ESTADO
,PRODUCTO
,No_DOCUMENTO
,NOMBRE_TITULAR
,CAPITAL_SOLICITADO
,CARGOS_ADMINISTRATIVOS
,CAPITAL_INICIAL
,PLAZO
,TASA_CLIENTE
,VALOR_CUOTACTE
,CARGOS_CUOTA
,VALOR_CUOTATOTAL
,CAPITALAMORTIZACION
,INTERESAMORTIZACION
,ESTADOCUOTA
,CTA
,FECHADESEMBOLSO
,FECHAVENCIMIENTOAMORTIZACION
,NUMEROCHEQUE
,ESTTITULO
,TIPODOCUMENTO
,FONDEADOR
,METODOLOGIA
,VALOR_NEGOCIADO
,VR_NEGOCIADO_SIN_SEGURO
,AMORTIZACION_SEGURO
,FECHA_VENTA
,TASA_VENTA
,METODOLOGIA_PAGO
,ESTADO_VENTA
,FECHA_VALORACION
,VPN
,CAPITAL_FONDEADOR
,INTERES_FONDEADOR
,SALDO_CAPITAL_FONDEADOR
,VENDIDO_CUOTA_TOTAL
,PAGO_CAPITAL_FONDEADOR
,PAGO_INTERES_FONDEADOR
,INTERES_PROYECT_FONDEADOR
,MORA
,GASTOS_DE_COBRANZA
,IVAGAC
)
SELECT 
PRE.CTIVO AS 'CREDITO'
,PRE.IDESTADO AS 'ESTADO'
,PRE.PRODUCTO AS 'PRODUCTO'
,PRE.NDOC AS 'No_DOCUMENTO'
,PER.NOMBRES AS 'NOMBRE_TITULAR'
,PRE.CAPITALSOLICITADO AS 'CAPITAL_SOLICITADO'
,ISNULL(ADM.VALOR,0) AS 'CARGOS_ADMINISTRATIVOS'
,PRE.CAPITALINICIAL AS 'CAPITAL_INICIAL'
,PRE.PLAZO AS 'PLAZO'
,PRE.INTERES AS 'TASA_CLIENTE'
,PRE.VALORCUOTACORRIENTE AS 'VALOR_CUOTACTE'
,ISNULL(CUO.VALOR,0) AS 'CARGOS_CUOTA'
,PRE.VALORCUOTATOTAL AS 'VALOR_CUOTATOTAL'
,AMT.CAPITAL AS 'CAPITALAMORTIZACION'
,AMT.INTERES AS 'INTERESAMORTIZACION'
,AMT.ESTADOCUOTA AS 'ESTADO_CUOTA_CLIENTE'
,AMT.CUOTA AS 'CTA'
,PRE.FECHADESEMBOLSO AS 'FECHADESEMBOLSO'
,AMT.FECHAVENCIMIENTO AS 'FECHAVENCIMIENTOAMORTIZACION'
,ISNULL(INFCHEQUE.NODOCUMENTO,'') AS 'NUMEROCHEQUE'
,CASE WHEN VXF.ESTADO='TERMINADO' THEN 'PAGADO'	
WHEN VXF.ESTADO='ACTIVO' AND AMT.FECHAVENCIMIENTO<@FECHAFINAL AND AMT.TIPOF='F' THEN 'VENCIDO'
WHEN VXF.ESTADO='ACTIVO' AND AMT.TIPOF='P' THEN 'PAGADO'
WHEN VXF.ESTADO='ACTIVO' THEN 'VIGENTE'
ELSE ''
END AS 'ESTTITULO'
,ISNULL(INFCHEQUE.TIPODOCUMENTO,'') AS 'TIPODOCUMENTO'
,ISNULL(FOND.NOMBRE,EMP.NOMBRES) AS 'FONDEADOR'
,ISNULL(FOND.METODOLOGIA,'') AS 'METODOLOGIA'
,ISNULL(AMT.VALORNEGOCIADOTOTAL,0) AS 'VALOR_NEGOCIADO'
,ISNULL(AMT.VALORNEGOCIADOCORRIENTE,0) AS 'VR_NEGOCIADO_SIN_SEGURO'
,ISNULL(AMT.VALORNEGOCIADOTOTAL,0)-ISNULL(AMT.VALORNEGOCIADOCORRIENTE,0) AS 'AMORTIZACION_SEGURO'
,ISNULL(VXF.FCOMPRA,'1900-01-01') AS 'FECHA_VENTA'
,ISNULL(VXF.TASA,'0') AS 'TASA_VENTA'
,ISNULL(METVENTA.DESCRIPCION,'PROPIO') AS 'METODOLOGIA_PAGO'
,ISNULL(VXF.ESTADO,'') AS 'ESTADO_VENTA'
,@FECHAFINAL AS 'FECHA_VALORACION'
,CASE
WHEN VXF.ESTADO='TERMINADO' THEN 0
WHEN VXF.ESTADO='ACTIVO' AND (AMT.TIPOF='P' OR AMT.TIPOF='') THEN 0
WHEN VXF.ESTADO='ACTIVO' THEN ISNULL(AMT.VPN,0)
ELSE 0
END AS 'VPN'
,CASE
WHEN VXF.ESTADO='TERMINADO' THEN ISNULL(AMT.CAPITALFON,0)
WHEN VXF.ESTADO='ACTIVO' THEN ISNULL(AMT.CAPITALFON,0)
ELSE 0
END AS 'CAPITAL_FONDEADOR'
,CASE
WHEN VXF.ESTADO='TERMINADO' THEN AMT.INTERESFON
WHEN VXF.ESTADO='ACTIVO' THEN AMT.INTERESFON
ELSE 0
END AS 'INTERES_FONDEADOR'
,CASE
WHEN VXF.ESTADO='TERMINADO' THEN AMT.SALDOFONDEADOR
WHEN VXF.ESTADO='ACTIVO' THEN AMT.SALDOFONDEADOR
ELSE 0
END AS 'SALDO_CAPITAL_FONDEADOR'
,CASE 
WHEN VXF.CUOTATOTAL='TRUE' THEN 'SI'
ELSE 'NO' 
END AS 'VENDIDO_CUOTA_TOTAL'
,ISNULL(KPG.Valor,0) AS 'PAGO_CAPITAL_FONDEADOR'
,ISNULL(IPG.Valor,0) AS 'PAGO_INTERES_FONDEADOR'
,0 AS 'INTERES_PROYECT_FONDEADOR'
,AMT.MORA AS 'MORA'
,AMT.GASTOS_DE_COBRANZA AS 'GASTOS_DE_COBRANZA'
,AMT.IVAGAC AS 'IVAGAC'
FROM #AMORTIZACIONCREDITO AMT WITH(NOLOCK)
INNER JOIN Prstms PRE WITH(NOLOCK) ON AMT.IDKATIOS=PRE.IDKATIOS AND AMT.IDPRESTAMO=PRE.IDPRESTAMO
INNER JOIN PERSONAS PER WITH(NOLOCK) ON PER.IDKATIOS=PRE.IDKATIOS AND PRE.TDOC=PER.TDOC AND PRE.NDOC=PER.NDOC
LEFT JOIN #CCARGOSADMIN ADM WITH(NOLOCK) ON AMT.IDKATIOS=ADM.IDKATIOS AND AMT.IDPRESTAMO=ADM.IDPRESTAMO
LEFT JOIN #CCARGOSCUOTA CUO WITH(NOLOCK) ON AMT.IDKATIOS=CUO.IDKATIOS AND AMT.IDPRESTAMO=CUO.IDPRESTAMO
INNER JOIN #DESEMBOLSOS DS WITH(NOLOCK) ON AMT.IDKATIOS=DS.IdKatios AND AMT.IdPrestamo=DS.IdPrestamo
LEFT JOIN AMORTIZACION INFCHEQUE WITH(NOLOCK) ON AMT.IDKATIOS=INFCHEQUE.IDKATIOS AND AMT.IDPRESTAMO=INFCHEQUE.IDPRESTAMO and INFCHEQUE.CUOTA=AMT.CUOTA  AND INFCHEQUE.IDDIARIO=DS.IDDIARIO
LEFT JOIN VENTAXFONDO VXF WITH(NOLOCK) ON PRE.IDKATIOS=VXF.IDKATIOS AND VXF.IDPRESTAMO=PRE.IDPRESTAMO AND VXF.PROYECTO=AMT.VENTA
LEFT JOIN FONDEADOR FON WITH(NOLOCK) ON FON.IDKATIOS=VXF.IDKATIOS AND FON.TDOC=VXF.TDOCF AND FON.NDOC=VXF.NDOCF
LEFT JOIN TBLPARAMETROS METVENTA WITH(NOLOCK) ON METVENTA.GRUPO='9' AND METVENTA.IDKATIOS='TECFINANZAS' AND METVENTA.NIVEL=VXF.METODOLOGIAPAGO
LEFT JOIN #KPAGADO KPG WITH(NOLOCK) ON AMT.IdKatios=KPG.IdKatios AND AMT.IdPrestamo=KPG.IdPrestamo AND AMT.Cuota=KPG.Cuota
LEFT JOIN #IPAGADO IPG WITH(NOLOCK) ON AMT.IdKatios=IPG.IdKatios AND AMT.IdPrestamo=IPG.IdPrestamo AND AMT.Cuota=IPG.Cuota
LEFT JOIN #GETFONDEADOR FOND WITH(NOLOCK) ON PRE.IdKatios=FOND.IDKATIOS AND PRE.IdPrestamo=FOND.IDPRESTAMO
INNER JOIN KATIOS KAT WITH(NOLOCK) ON PRE.IDKATIOS=KAT.IDKATIOS
INNER JOIN PERSONAS EMP WITH(NOLOCK) ON PRE.IDKATIOS=EMP.IDKATIOS AND KAT.IUEMPRESA=EMP.NDOC AND KAT.TDOCIUEmpresa=EMP.TDOC
WHERE PRE.IDKATIOS=@IDKATIOS 
AND PRE.PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos')
AND PRE.CTIVO>0 
AND PRE.IdPrestamo IN (SELECT VALUE FROM SPLIT (',',@IDPRESTAMOS)) 
ORDER BY PRE.CTIVO,CAST(AMT.CUOTA AS INT)
END
