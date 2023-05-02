USE K003
DECLARE  @IDKATIOS  CHAR(20),
		 @FECHAINI DATE,
	     @FECHAFIN DATE,
		 @MES VARCHAR(5) = SUBSTRING(CONVERT(VARCHAR(10), GETDATE(), 120),6,2),
         @MESANTERIOR INT,
		 @ANIO VARCHAR(6) = LEFT(CONVERT(VARCHAR(10), GETDATE(), 120),4)

SET @IDKATIOS = 'DELTA'

IF @MES != '01'
	SET @MESANTERIOR = CONVERT(INT, @MES)-1;
ELSE 
	BEGIN
	SET @MESANTERIOR = CONVERT(INT, @MES)+11;
	SET @ANIO = @ANIO - 1
	END

SET @MES = CONVERT(VARCHAR, @MESANTERIOR);

IF LEN(@MES) = 1
	SET @MES = '0'+@MES

SET	@FECHAINI = @ANIO + '-' + @MES + '-01'
SET	@FECHAFIN = @ANIO + '-' + @MES + '-' +  LEFT(CONVERT(VARCHAR(25),DATEADD(dd,-(DAY(GETDATE())),GETDATE()),105),2)  

IF OBJECT_ID('tempdb..#CuotasCausacionTemporal') IS NOT NULL  
BEGIN  
	DROP TABLE #CuotasCausacionTemporal;
END
CREATE TABLE #CuotasCausacionTemporal
(
[CREDITO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[PRODUCTO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[No_DOCUMENTO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[NOMBRE_TITULAR] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[FECHA_INICIAL] DATE
,[CORTE] INT
,[FECHA_DESEMBOLSO] DATE
,[FECHA_PRIMERVCTO] DATE
,[CAPITAL_INICIAL] NUMERIC(18,2)
,[PLAZO] INT
,[TASANM_CREDITO] DECIMAL(18,16)
,[CUOTA_CORRIENTE] NUMERIC(18,2)
,[CUOTA_TOTAL] NUMERIC(18,2)
,[No_CUOTA_CAUSADA] INT
,[FECHA_CUOTA_CAUSADA] DATE
,[INTERESES_CORRIENTES] NUMERIC(18,2)
,[SEGURO] NUMERIC(18,2)
,[PERIODO_GRACIA] NUMERIC(18,2)
,[GAC] NUMERIC(18,2)
,[IVAGAC] NUMERIC(18,2)
,[INTERES_MORA] NUMERIC(18,2)
,[GPS] NUMERIC(18,2)
,[BUSURA] NUMERIC(18,2)
,[TASA_USURA] DECIMAL(18,16)
)

INSERT INTO #CuotasCausacionTemporal
SELECT
PRE.CTIVO AS 'CREDITO'
,PRE.PRODUCTO AS 'PRODUCTO'
,PER.NDOC AS 'No_DOCUMENTO'
,PER.NOMBRES AS 'NOMBRE_TITULAR'
,PRE.FECHAINICIAL AS 'FECHA_INICIAL'
,DAY(PRE.FECHAINICIAL) AS 'CORTE'
,PRE.FECHADESEMBOLSO AS 'FECHA_DESEMBOLSO'
,DATEADD(MONTH,1,PRE.FECHAINICIAL) AS 'FECHA_PRIMERVCTO'
,PRE.CAPITALINICIAL AS 'CAPITAL_INICIAL'
,PRE.PLAZO AS 'PLAZO'
,PRE.INTERES AS 'TASANM_CREDITO'
,PRE.VALORCUOTACORRIENTE AS 'CUOTA_CORRIENTE'
,PRE.VALORCUOTATOTAL AS 'CUOTA_TOTAL'
,PD.DEBITO AS 'No_CUOTA_CAUSADA'
,DATEADD(MONTH,PD.DEBITO,PRE.FECHAINICIAL) AS 'FECHA_CUOTA_CAUSADA'
,ISNULL(IC.DEBITO,0) AS 'INTERESES_CORRIENTES'
,ISNULL(SC.DEBITO,0) AS 'SEGURO'
,ISNULL(PGC.DEBITO,0) AS 'PERIODO_GRACIA'
,ISNULL(GC.VALOR,0) AS 'GAC'
,ISNULL(IGC.VALOR,0) AS 'IVAGAC'
,ISNULL(IMC.VALOR,0) AS 'INTERES_MORA'
,ISNULL(CXCM.VALOR,0) AS 'GPS'
,ISNULL(BU.Credito,0) AS 'BUSURA'
,ISNULL(TU.VALOR,PRE.INTERES) AS 'TASA_USURA'
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN PERSONAS PER WITH(NOLOCK) ON PRE.IDKATIOS=PER.IDKATIOS AND PRE.TDOC=PER.TDOC AND PRE.NDOC=PER.NDOC
INNER JOIN PRSTMSENC PE WITH(NOLOCK) ON PRE.IDKATIOS=PE.IDKATIOS AND PRE.IDPRESTAMO=PE.IDPRODUCTO AND PE.IDTRX='5005' AND PE.REFERENCIA NOT LIKE 'RV%'
INNER JOIN PRSTMSDETALLE PD WITH(NOLOCK) ON PRE.IDKATIOS=PD.IDKATIOS AND PRE.IDPRESTAMO=PD.IDPRESTAMO AND PE.IDDIARIO=PD.IDDIARIO AND PE.IDENCABEZADO=PD.IDENCABEZADO AND PD.NOMBRECUENTA='Ccausadas'
INNER JOIN DIARIO DRO WITH(NOLOCK) ON PRE.IDKATIOS=DRO.IDKATIOS AND PE.IDDIARIO=DRO.IDDIARIO AND DRO.TIPOTRX<>'RV'
INNER JOIN CONTADETALLE IC WITH(NOLOCK) ON PRE.IDKATIOS=IC.IDKATIOS AND PE.IDDIARIO=IC.IDDIARIO AND IC.MEMO='CXC INTERES CORRIENTE'
INNER JOIN CONTADETALLE SC WITH(NOLOCK) ON PRE.IDKATIOS=SC.IDKATIOS AND PE.IDDIARIO=SC.IDDIARIO AND SC.MEMO='CXC SEGURO'
INNER JOIN CONTADETALLE PGC WITH(NOLOCK) ON PRE.IDKATIOS=PGC.IDKATIOS AND PE.IDDIARIO=PGC.IDDIARIO AND PGC.MEMO='INTERESES POR DIFERIR PERIODO DE GRACIA'
INNER JOIN AMORTIZACIONVARIABLE GC WITH(NOLOCK) ON PRE.IDKATIOS=GC.IDKATIOS AND PRE.IDPRESTAMO=GC.IDPRESTAMO AND GC.CUOTA=PD.DEBITO AND GC.CONCEPTO='GAC'
INNER JOIN AMORTIZACIONVARIABLE IGC WITH(NOLOCK) ON PRE.IDKATIOS=IGC.IDKATIOS AND PRE.IDPRESTAMO=IGC.IDPRESTAMO AND IGC.CUOTA=PD.DEBITO AND IGC.CONCEPTO='IVAGAC'
INNER JOIN AMORTIZACIONVARIABLE IMC WITH(NOLOCK) ON PRE.IDKATIOS=IMC.IDKATIOS AND PRE.IDPRESTAMO=IMC.IDPRESTAMO AND IMC.CUOTA=PD.DEBITO AND IMC.CONCEPTO='IMORA'
LEFT JOIN PRSTMSDETALLE BU WITH(NOLOCK) ON PRE.IDKATIOS=BU.IDKATIOS AND PRE.IDPRESTAMO=BU.IDPRESTAMO AND PE.IDDIARIO=BU.IDDIARIO AND PE.IDENCABEZADO=BU.IDENCABEZADO AND BU.NOMBRECUENTA='BUsura'
LEFT JOIN USURA TU WITH(NOLOCK) ON PRE.IDKATIOS=BU.IDKATIOS AND  DRO.FECHAEFECTIVA BETWEEN TU.FECHAI AND TU.FECHAF
LEFT JOIN CONCEPTOSXFONDO II WITH(NOLOCK) ON PRE.IDKATIOS=II.IDKATIOS AND PRE.IDPRESTAMO=II.IDPRESTAMO AND II.NOMBRE='CXCINTINICIALES'
LEFT JOIN CONCEPTOSXFONDO RU WITH(NOLOCK) ON PRE.IDKATIOS=RU.IDKATIOS AND PRE.IDPRESTAMO=RU.IDPRESTAMO AND RU.NOMBRE='CXCRUNT'
LEFT JOIN CONCEPTOSXFONDO GM WITH(NOLOCK) ON PRE.IDKATIOS=GM.IDKATIOS AND PRE.IDPRESTAMO=GM.IDPRESTAMO AND GM.NOMBRE='CXCGARANTIASM'
LEFT JOIN CONCEPTOSXFONDO IGM WITH(NOLOCK) ON PRE.IDKATIOS=IGM.IDKATIOS AND PRE.IDPRESTAMO=IGM.IDPRESTAMO AND IGM.NOMBRE='CXCIVAGM'
LEFT JOIN CONCEPTOSXFONDO CXCIN WITH(NOLOCK) ON PRE.IdKatios=CXCIN.IDKATIOS AND PRE.IdPrestamo=CXCIN.IdPrestamo AND CXCIN.NOMBRE='CXCCGPS'
LEFT JOIN PRESTAMOSCARGOS CXCM WITH(NOLOCK) ON PRE.IdKatios=CXCM.IDKATIOS AND PRE.IdPrestamo=CXCM.IdPrestamo AND CXCM.NOMBRE='GPS'
WHERE PRE.IDKATIOS=@IDKATIOS
AND DRO.FECHAEFECTIVA BETWEEN @FECHAINI AND @FECHAFIN
ORDER BY DRO.FECHAEFECTIVA,PRE.CTIVO

USE K003_2
CREATE TABLE CuotasCausacion
(
[CREDITO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[PRODUCTO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[No_DOCUMENTO] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[NOMBRE_TITULAR] VARCHAR(100) COLLATE Modern_Spanish_CI_AS
,[FECHA_INICIAL] DATE
,[CORTE] INT
,[FECHA_DESEMBOLSO] DATE
,[FECHA_PRIMERVCTO] DATE
,[CAPITAL_INICIAL] NUMERIC(18,2)
,[PLAZO] INT
,[TASANM_CREDITO] DECIMAL(18,16)
,[CUOTA_CORRIENTE] NUMERIC(18,2)
,[CUOTA_TOTAL] NUMERIC(18,2)
,[No_CUOTA_CAUSADA] INT
,[FECHA_CUOTA_CAUSADA] DATE
,[INTERESES_CORRIENTES] NUMERIC(18,2)
,[SEGURO] NUMERIC(18,2)
,[PERIODO_GRACIA] NUMERIC(18,2)
,[GAC] NUMERIC(18,2)
,[IVAGAC] NUMERIC(18,2)
,[INTERES_MORA] NUMERIC(18,2)
,[GPS] NUMERIC(18,2)
,[BUSURA] NUMERIC(18,2)
,[TASA_USURA] DECIMAL(18,16)
)

INSERT INTO CuotasCausacion
SELECT
cc.CREDITO AS 'CREDITO'
,cc.PRODUCTO AS 'PRODUCTO'
,cc.No_DOCUMENTO AS 'No_DOCUMENTO'
,cc.NOMBRE_TITULAR AS 'NOMBRE_TITULAR'
,cc.FECHA_INICIAL AS 'FECHA_INICIAL'
,cc.CORTE AS 'CORTE'
,cc.FECHA_DESEMBOLSO AS 'FECHA_DESEMBOLSO'
,cc.FECHA_PRIMERVCTO AS 'FECHA_PRIMERVCTO'
,cc.CAPITAL_INICIAL AS 'CAPITAL_INICIAL'
,cc.PLAZO AS 'PLAZO'
,cc.TASANM_CREDITO AS 'TASANM_CREDITO'
,cc.CUOTA_CORRIENTE AS 'CUOTA_CORRIENTE'
,cc.CUOTA_TOTAL AS 'CUOTA_TOTAL'
,cc.No_CUOTA_CAUSADA AS 'No_CUOTA_CAUSADA'
,cc.FECHA_CUOTA_CAUSADA AS 'FECHA_CUOTA_CAUSADA'
,cc.INTERESES_CORRIENTES AS 'INTERESES_CORRIENTES'
,cc.SEGURO AS 'SEGURO'
,cc.PERIODO_GRACIA AS 'PERIODO_GRACIA'
,cc.GAC AS 'GAC'
,cc.IVAGAC AS 'IVAGAC'
,cc.INTERES_MORA AS 'INTERES_MORA'
,cc.GPS AS 'GPS'
,cc.BUSURA AS 'BUSURA'
,cc.TASA_USURA AS 'TASA_USURA'
FROM #CuotasCausacionTemporal cc WITH(NOLOCK)
