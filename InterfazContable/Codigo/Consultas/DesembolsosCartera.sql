USE K003
DECLARE @IDKATIOS CHAR(20),
@FECHAINI DATE,
@FECHAFIN DATE

SET @IDKATIOS = 'DELTA'
SET @FECHAINI = LEFT (CONVERT(VARCHAR(10), GETDATE(), 120),8) + '01'
SET @FECHAFIN = LEFT (CONVERT(VARCHAR(10), GETDATE(), 120),8) + RIGHT(EOMONTH(@FECHAINI),2)

IF OBJECT_ID('tempdb..#DesembolsoCarteraTemporal') IS NOT NULL  
   BEGIN  
    DROP TABLE #DesembolsoCarteraTemporal;
END
CREATE TABLE #DesembolsoCarteraTemporal
(
[FECHA ORIGINACION] DATE
,[FECHA INICIAL] DATE
,[DIA VENCIMIENTO] INT
,[PRIMERA FECHA VENCIMIENTO] DATE
,[PRODUCTO] VARCHAR(100) 
,[OFICINA] VARCHAR(100) 
,[ESTADO] VARCHAR(100)
,[NoCREDITO] VARCHAR(100)
,[CEDULA] VARCHAR(100) 
,[NOMBRE] VARCHAR(100) 
,[COMERCIAL] VARCHAR(100)
,[CONCESIONARIO] VARCHAR(100) 
,[VENDEDOR] VARCHAR(100) 
,[CAPITAL INICIAL] NUMERIC(18,2) 
,[PLAZO] VARCHAR(100) 
,[TASA CLIENTE] DECIMAL(4,1)
,[CUOTA CTE] NUMERIC(18,2)
,[CARGOS CUOTA] NUMERIC(18,2) 
,[CUOTA TOTAL] NUMERIC(18,2)
,[CXC VALOR TOTAL PERIODO DE GRACIA] NUMERIC(18,2)
,[CXC VALOR MENSUAL PGRACIA] NUMERIC(18,2)
,[CXC INTERESES INICIALES] NUMERIC(18,2)
,[RUNT] NUMERIC(18,2)
,[GARANTIAS M] NUMERIC(18,2)
,[IVA GM] NUMERIC(18,2)
,[MARCA] VARCHAR(100) 
,[PLACA] VARCHAR(100) 
,[MODELO] VARCHAR(100)
,[CLASE] VARCHAR(100) 
,[PERIODOSGRACIA] VARCHAR(100) 
)
INSERT INTO #DesembolsoCarteraTemporal
SELECT DISTINCT
PRE.FechaDesembolso AS 'FECHA ORIGINACION'
,PRE.FechaInicial AS 'FECHA INICIAL'
,DAY(PRE.FechaInicial) AS 'DIA VENCIMIENTO'
,DATEADD(MONTH, 1, PRE.FechaInicial) AS 'PRIMERA FECHA VENCIMIENTO'
,ISNULL(PRE.Producto,'') AS 'PRODUCTO'
,ISNULL(OFC.OFUbicacion,'') AS 'OFICINA'
,ISNULL(PRE.IdEstado,'') AS 'ESTADO'
,ISNULL(PRE.Ctivo,'0') AS 'NoCREDITO'
,ISNULL(PER.NDoc,'0') AS 'CEDULA'
,ISNULL(PER.Nombres,'') AS 'NOMBRE'
,ISNULL(COM.Nombres,'') AS 'COMERCIAL'
,ISNULL(VD4.Descripcion,'') AS 'CONCESIONARIO'
,ISNULL(VD5.Descripcion,'') AS 'VENDEDOR'
,ISNULL(PRE.SaldoDesembolsado,'0') AS 'CAPITAL INICIAL'
,ISNULL(PRE.Plazo,'0') AS 'PLAZO'
,ISNULL(PRE.Interes,'0') AS 'TASA CLIENTE'
,ISNULL(PRE.ValorCuotaCorriente,'0') AS 'CUOTA CTE'
,ISNULL(PCS.Valor,'0') AS 'CARGOS CUOTA'
,ISNULL(PRE.ValorCuotaTotal,'0') AS 'CUOTA TOTAL' 
,ISNULL(CXCPG.PAGADO,'0') AS 'CXC VALOR TOTAL PERIODO DE GRACIA' 
,ISNULL(PG.Valor,'0') AS 'CXC VALOR MENSUAL PGRACIA'
,ISNULL(CXCI.PAGADO,'0') AS 'CXC INTERESES INICIALES'
,ISNULL(CXCRUNT.PAGADO,'0') AS 'RUNT' 
,ISNULL(CXCGM.PAGADO,'0') AS 'GARANTIAS M'
,ISNULL(CXCIVA.PAGADO,'0') AS 'IVA GM'
,ISNULL(VD.Valor,'') AS 'MARCA'
,ISNULL(VD1.Valor,'') AS 'PLACA'
,ISNULL(VD2.Valor,'') AS 'MODELO'
,ISNULL(VD3.Valor,'') AS 'CLASE'
,ISNULL(PG.ValorCargo,0) AS 'PERIODOSGRACIA'
FROM PRSTMS PRE WITH(NOLOCK)
INNER JOIN Oficinas OFC WITH(NOLOCK) ON PRE.IdKatios=OFC.IdKatios AND PRE.OFCodigo=OFC.OFCodigo 
INNER JOIN Personas PER WITH(NOLOCK) ON PRE.IdKatios=PER.IdKatios AND PRE.TDoc=PER.TDoc AND PRE.NDoc=PER.NDoc
LEFT JOIN Personas COM WITH(NOLOCK) ON PRE.IdKatios=COM.IdKatios AND PRE.Comercial=COM.TDoc+'-'+COM.NDoc
INNER JOIN PRSTMSENC PE WITH(NOLOCK) ON PRE.IDKATIOS=PE.IDKATIOS AND PRE.IDPRESTAMO=PE.IDPRODUCTO AND PE.IDTRX='5007' AND PE.REFERENCIA NOT LIKE 'RV%' --LA TRX ES LAS 5007
INNER JOIN DIARIO DRO WITH(NOLOCK) ON PRE.IDKATIOS=DRO.IDKATIOS AND PE.IDDIARIO=DRO.IDDIARIO AND DRO.TIPOTRX<>'RV'
LEFT JOIN PrestamosCargos PCS WITH(NOLOCK) ON PRE.IdKatios=PCS.IdKatios AND PRE.IdPrestamo=PCS.IdPrestamo AND PCS.Nombre='SEGURO'
LEFT JOIN PrestamosCargos PG WITH(NOLOCK) ON PRE.IdKatios=PG.IdKatios AND PRE.IdPrestamo=PG.IdPrestamo AND PG.Nombre='PGRACIA'
LEFT JOIN ValoresCapturasDinamicas VD WITH(NOLOCK) ON PRE.IdKatios=VD.IdKatios AND PRE.Solicitud=VD.NoProducto AND VD.IdCaptura='EST_01_1' AND VD.Descripcion='Fasecolda_Marca'
LEFT JOIN ValoresCapturasDinamicas VD1 WITH(NOLOCK) ON PRE.IdKatios=VD1.IdKatios AND PRE.Solicitud=VD1.NoProducto AND VD1.IdCaptura='EST_01_1' AND VD1.Descripcion='Placa'
LEFT JOIN ValoresCapturasDinamicas VD2 WITH(NOLOCK) ON PRE.IdKatios=VD2.IdKatios AND PRE.Solicitud=VD2.NoProducto AND VD2.IdCaptura='EST_01_1' AND VD2.Descripcion='Fasecolda_Modelo'
LEFT JOIN ValoresCapturasDinamicas VD3 WITH(NOLOCK) ON PRE.IdKatios=VD3.IdKatios AND PRE.Solicitud=VD3.NoProducto AND VD3.IdCaptura='EST_01_1' AND VD3.Descripcion='Fasecolda_Clase'
LEFT JOIN ValoresCapturasDinamicas VD4 WITH(NOLOCK) ON PRE.IdKatios=VD4.IdKatios AND PRE.Solicitud=VD4.NoProducto AND VD4.IdCaptura='ASC 0001'
LEFT JOIN ValoresCapturasDinamicas VD5 WITH(NOLOCK) ON PRE.IdKatios=VD5.IdKatios AND PRE.Solicitud=VD5.NoProducto AND VD5.IdCaptura='ASC 0003'
LEFT JOIN CONCEPTOSXFONDO CXCPG WITH(NOLOCK) ON PRE.IdKatios=CXCPG.IDKATIOS AND PRE.IdPrestamo=CXCPG.IdPrestamo AND CXCPG.NOMBRE='CXCPGRACIA'
LEFT JOIN CONCEPTOSXFONDO CXCI WITH(NOLOCK) ON PRE.IdKatios=CXCI.IDKATIOS AND PRE.IdPrestamo=CXCI.IdPrestamo AND CXCI.NOMBRE='CXCINTINICIALES'
LEFT JOIN CONCEPTOSXFONDO CXCRUNT WITH(NOLOCK) ON PRE.IdKatios=CXCRUNT.IDKATIOS AND PRE.IdPrestamo=CXCRUNT.IdPrestamo AND CXCRUNT.NOMBRE='CXCRUNT'
LEFT JOIN CONCEPTOSXFONDO CXCGM WITH(NOLOCK) ON PRE.IdKatios=CXCGM.IDKATIOS AND PRE.IdPrestamo=CXCGM.IdPrestamo AND CXCGM.NOMBRE='CXCGARANTIASM'
LEFT JOIN CONCEPTOSXFONDO CXCIVA WITH(NOLOCK) ON PRE.IdKatios=CXCIVA.IDKATIOS AND PRE.IdPrestamo=CXCIVA.IdPrestamo AND CXCIVA.NOMBRE='CXCIVAGM'
WHERE PRE.IDKATIOS=@IDKATIOS
AND PRE.Producto NOT IN ('Venta Cuota Creciente','Venta de Flujos')
AND PRE.FechaDesembolso BETWEEN @FECHAINI AND @FECHAFIN
ORDER BY PRE.FechaDesembolso 

USE K003_2
IF OBJECT_ID('tempdb..DesembolsoCartera') IS NOT NULL  
   BEGIN  
    DROP TABLE DesembolsoCartera;
END
CREATE TABLE DesembolsoCartera
(
[FECHA ORIGINACION] DATE
,[FECHA INICIAL] DATE
,[DIA VENCIMIENTO] INT
,[PRIMERA FECHA VENCIMIENTO] DATE
,[PRODUCTO] VARCHAR(100) 
,[OFICINA] VARCHAR(100) 
,[ESTADO] VARCHAR(100)
,[NoCREDITO] VARCHAR(100)
,[CEDULA] VARCHAR(100) 
,[NOMBRE] VARCHAR(100) 
,[COMERCIAL] VARCHAR(100)
,[CONCESIONARIO] VARCHAR(100) 
,[VENDEDOR] VARCHAR(100) 
,[CAPITAL INICIAL] NUMERIC(18,2) 
,[PLAZO] VARCHAR(100) 
,[TASA CLIENTE] DECIMAL(4,1)
,[CUOTA CTE] NUMERIC(18,2)
,[CARGOS CUOTA] NUMERIC(18,2) 
,[CUOTA TOTAL] NUMERIC(18,2)
,[CXC VALOR TOTAL PERIODO DE GRACIA] NUMERIC(18,2)
,[CXC VALOR MENSUAL PGRACIA] NUMERIC(18,2)
,[CXC INTERESES INICIALES] NUMERIC(18,2)
,[RUNT] NUMERIC(18,2)
,[GARANTIAS M] NUMERIC(18,2)
,[IVA GM] NUMERIC(18,2)
,[MARCA] VARCHAR(100) 
,[PLACA] VARCHAR(100) 
,[MODELO] VARCHAR(100)
,[CLASE] VARCHAR(100) 
,[PERIODOSGRACIA] VARCHAR(100) 
)
INSERT INTO DesembolsoCartera
SELECT DISTINCT
dc.[FECHA ORIGINACION] AS 'FECHA ORIGINACION'
,dc.[FECHA INICIAL] AS 'FECHA INICIAL'
,dc.[DIA VENCIMIENTO] AS 'DIA VENCIMIENTO'
,dc.[PRIMERA FECHA VENCIMIENTO] AS 'PRIMERA FECHA VENCIMIENTO'
,dc.[PRODUCTO] AS 'PRODUCTO'
,dc.[OFICINA] AS 'OFICINA'
,dc.[ESTADO] AS 'ESTADO'
,dc.[NoCREDITO] AS 'NoCREDITO'
,dc.[CEDULA] AS 'CEDULA'
,dc.[NOMBRE] AS 'NOMBRE'
,dc.[COMERCIAL] AS 'COMERCIAL'
,dc.[CONCESIONARIO] AS 'CONCESIONARIO'
,dc.[VENDEDOR] AS 'VENDEDOR'
,dc.[CAPITAL INICIAL] AS 'CAPITAL INICIAL'
,dc.[PLAZO] AS 'PLAZO'
,dc.[TASA CLIENTE] AS 'TASA CLIENTE'
,dc.[CUOTA CTE] AS 'CUOTA CTE'
,dc.[CARGOS CUOTA] AS 'CARGOS CUOTA'
,dc.[CUOTA TOTAL] AS 'CUOTA TOTAL' 
,dc.[CXC VALOR TOTAL PERIODO DE GRACIA] AS 'CXC VALOR TOTAL PERIODO DE GRACIA' 
,dc.[CXC VALOR MENSUAL PGRACIA] AS 'CXC VALOR MENSUAL PGRACIA'
,dc.[CXC INTERESES INICIALES] AS 'CXC INTERESES INICIALES'
,dc.[RUNT] AS 'RUNT' 
,dc.[GARANTIAS M] AS 'GARANTIAS M'
,dc.[IVA GM] AS 'IVA GM'
,dc.[MARCA] AS 'MARCA'
,dc.[PLACA] AS 'PLACA'
,dc.[MODELO] AS 'MODELO'
,dc.[CLASE] AS 'CLASE'
,dc.[PERIODOSGRACIA] AS 'PERIODOSGRACIA'
FROM #DesembolsoCarteraTemporal dc WITH(NOLOCK)

