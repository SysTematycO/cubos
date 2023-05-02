USE K003
DECLARE @IDKATIOS CHAR(20)

SET @IDKATIOS = 'DELTA'

BEGIN

	SET NOCOUNT ON;

DECLARE  @SOLIDARIOS AS TABLE 
(
IDKATIOS VARCHAR(20)
,IDPRESTAMO VARCHAR(20)
,NDOC VARCHAR(20)
,TDOC VARCHAR(20)
,TIPO VARCHAR(30)
,ORDEN VARCHAR(10)
)

INSERT INTO @SOLIDARIOS
SELECT  
IDKATIOS
,IDPRESTAMO
,SOLIDARIO.value('(//Row/Documento)[1]', 'nvarchar(max)') NDOC
,SOLIDARIO.value('(//Row/TipoDoc)[1]', 'nvarchar(max)') TDOC
,SOLIDARIO.value('(//Row/Tipo)[1]', 'nvarchar(max)') TIPO
,RANK () OVER ( partition by IDPRESTAMO,SOLIDARIO.value('(//Row/Tipo)[1]', 'nvarchar(max)')  order by SOLIDARIO.value('(//Row/Documento)[1]', 'nvarchar(max)') ) ORDEN
FROM(
	SELECT IDKATIOS, IDPRESTAMO,
	CAST(x.query('.') AS XML) SOLIDARIO
	FROM(
		SELECT IDKATIOS,IDPRESTAMO,CAST(SOLIDARIOS AS XML) SOL
		FROM PRSTMS WITH(NOLOCK)
		WHERE IDKATIOS=@IDKATIOS AND IdEstado='ACTIVO'
	) T
	CROSS APPLY SOL.nodes('//SOLIDARIOS/Row') T2(x)
)T3

DECLARE  @DIRECCIONES AS TABLE 
(
IDKATIOS VARCHAR(20)
,TDOC VARCHAR(10)
,NDOC VARCHAR(20)
,CIUDAD VARCHAR(50)
, CODDANE VARCHAR(20)
,DIRECCION VARCHAR(120)
,BARRIO VARCHAR(50)
,DEPARTAMENTO VARCHAR(50)
,TELEFONO VARCHAR(30)
,ORDEN VARCHAR (10)
)

INSERT INTO @DIRECCIONES
SELECT DISTINCT
PDIR.IDKATIOS
,PDIR.TDOC
,PDIR.NDOC
,MAX(COD.CIUDAD)
,MAX(COD.CODIGO)
,MAX(PDIR.LINEA1+''+PDIR.LINEA2)
,MAX(PDIR.BARRIO)
,MAX(COD.DEPARTAMENTO)
,MAX(PDIR.TELEFONO)
,RANK () OVER (PARTITION BY PDIR.NDOC ORDER BY PDIR.NDOC)
FROM PDIRECCIONES PDIR WITH(NOLOCK)
INNER JOIN @SOLIDARIOS SOL ON PDIR.IDKATIOS=SOL.IDKATIOS COLLATE Modern_Spanish_CI_AS AND PDIR.TDOC=SOL.TDOC COLLATE Modern_Spanish_CI_AS AND PDIR.NDOC=SOL.NDOC COLLATE Modern_Spanish_CI_AS
LEFT JOIN CODIGOSDANE COD WITH(NOLOCK) ON PDIR.CODDANE=COD.CODIGO
WHERE PDIR.IDKATIOS=@IDKATIOS 
GROUP BY PDIR.IDKATIOS,PDIR.TDOC,PDIR.NDOC

DECLARE @REFERENCIAS AS TABLE
(
IDKATIOS VARCHAR(30)
,TDOC VARCHAR(10)
,NDOC VARCHAR(30)
,NOMBRE VARCHAR(MAX)
,CELULARREFERENCIA VARCHAR(20)
,EMAIL VARCHAR(MAX)
,TELEFONO VARCHAR(20)
,DIRECCION VARCHAR(MAX)
,TIPO VARCHAR(20)
,ORDEN VARCHAR(10)
,CIUDAD VARCHAR(MAX)
)

INSERT INTO  @REFERENCIAS
SELECT 
DISTINCT
R.IDKATIOS 
,R.TDOC 
,R.NDOC
,R.NOMBRE
,R.CELULARREFERENCIA
,R.EMAIL
,R.TELEFONO
,R.DIRECCION
,TBL.DESCRIPCION TIPO
,RANK() OVER( PARTITION BY R.NDOC,R.TIPOREFERENCIA ORDER BY R.IDKEY)
,COD.CIUDAD
FROM REFERENCIAS R WITH(NOLOCK)
INNER JOIN TBLPARAMETROS TBL WITH(NOLOCK) ON TBL.GRUPO=21 AND TBL.NIVEL=R.TIPOREFERENCIA
LEFT JOIN CODIGOSDANE COD WITH(NOLOCK) ON R.CIUDAD=COD.CODIGO
WHERE R.IDKATIOS=@IDKATIOS 

DECLARE @CONYUGE AS TABLE
(
IDKATIOS VARCHAR(30) 
,IDPRESTAMO  VARCHAR(30) 
,TDOC VARCHAR(20)
,NDOC VARCHAR(30) 
,TIPO VARCHAR(20)
)

INSERT INTO @CONYUGE
SELECT 
PNG.IDKATIOS IDKATIOS
,P.IDPRESTAMO IDPRESTAMO
,PNG.PERNTDOCCYG TDOC
,PERNDOCCYG NDOC
,'Conyuge' TIPO
 FROM PRSTMS P WITH(NOLOCK)
INNER JOIN PNGeneral PNG WITH(NOLOCK) ON P.IDKATIOS=PNG.IDKATIOS AND P.TDOC=PNG.TDOC AND P.NDoc=PNG.NDoc
WHERE PNG.IDKATIOS=@IDKATIOS 
AND P.IDESTADO='ACTIVO'
AND P.PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos')

DECLARE @TABLAGENERAL AS TABLE
(
TIPO VARCHAR (MAX)
,CREDITO VARCHAR (MAX)
,TDOCUMENTO VARCHAR (MAX)
,NDOCUMENTO	VARCHAR (MAX)
,NOMBRES VARCHAR (MAX)
,APELLIDOS VARCHAR (MAX)
,CELULAR	VARCHAR (MAX)
,EMAIL VARCHAR (MAX)
,TELEFONO VARCHAR (MAX)
,DIRECCION VARCHAR (MAX)
,BARRIO VARCHAR (MAX)
,CIUDAD VARCHAR (MAX)
,DEPARTAMENTO VARCHAR (MAX)
,PERFECHANACIMIENTO VARCHAR (MAX)
)

INSERT INTO @TABLAGENERAL
SELECT 
SOL.TIPO
,CAST( P.Ctivo AS VARCHAR) CREDITO
,SOL.TDOC TDOCUMENTO
,SOL.NDOC NDOCUMENTO
,CASE WHEN SOL.TDOC='TDOC' THEN PER.NOMBRES ELSE PNG.PERNOMBRES END NOMBRES
,CASE WHEN SOL.TDOC='3' THEN '' ELSE PNG.PERApellidos END APELLIDOS
,PER.Celular CELULAR
,PER.Email EMAIL
,DIR.TELEFONO TELEFONO
,DIR.DIRECCION DIRECCION
,DIR.BARRIO
,DIR.CIUDAD
,DIR.DEPARTAMENTO
,PNG.PERFechaNacimiento
FROM Prstms P WITH(NOLOCK)
LEFT JOIN @SOLIDARIOS SOL ON P.IDKATIOS=SOL.IDKATIOS  AND P.IDPRESTAMO=SOL.IDPRESTAMO AND SOL.ORDEN='1'
LEFT JOIN PNGeneral PNG WITH(NOLOCK) ON PNG.IDKATIOS=SOL.IDKATIOS AND PNG.TDoc=SOL.TDOC AND PNG.NDOC=SOL.NDOC
LEFT JOIN Personas PER WITH(NOLOCK) ON PER.IDKATIOS=SOL.IDKATIOS AND PER.TDoc=SOL.TDOC AND PER.NDOC=SOL.NDOC
LEFT JOIN @DIRECCIONES DIR ON DIR.IDKATIOS=SOL.IdKatios AND SOL.NDOC=DIR.NDOC AND SOL.TDOC=DIR.TDOC
WHERE P.IdKatios=@IDKATIOS
AND P.PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos')

UNION ALL
SELECT DISTINCT
REF.TIPO
,P.CTIVO
,''
,'' 
,REF.NOMBRE
,''
,REF.CELULARREFERENCIA
,REF.EMAIL
,REF.TELEFONO
,REF.DIRECCION
,''
,REF.CIUDAD
,''
,''
FROM Prstms P WITH(NOLOCK)
INNER JOIN @REFERENCIAS REF ON REF.IDKATIOS=P.IdKatios AND P.TDoc=REF.TDOC AND P.NDoc=REF.NDOC AND REF.ORDEN='1'
WHERE P.IdKatios=@IDKATIOS
AND P.IdEstado='ACTIVO'
AND P.PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos')

UNION ALL
SELECT 
CYG.TIPO
,cast( P.Ctivo as varchar) CREDITO
,ISNULL(CYG.TDOC,'') TDOCUMENTO
,ISNULL(CYG.NDOC,'')  NDOCUMENTO
,ISNULL(PNGCYG.PERNombres,'')  NOMBRES
,ISNULL(PNGCYG.PERApellidos,'')  APELLIDOS
,ISNULL(PERCYG.celular,'')  CELULAR
,ISNULL(perCYG.email,'')  EMAIL
,ISNULL(DIRCYG.TELEFONO,'')  TELEFONO
,ISNULL(DIRCYG.DIRECCION,'')  DIRECCION
,ISNULL(DIRCYG.BARRIO,'')  BARRIO
,ISNULL(DIRCYG.CIUDAD,'')  CIUDAD
,ISNULL(DIRCYG.DEPARTAMENTO,'')  DEPARTAMENTO
,ISNULL(PNGCYG.PERFechaNacimiento,'') FNACIMIENTO
FROM Prstms P WITH(NOLOCK)
LEFT JOIN @CONYUGE CYG ON P.IDKATIOS=CYG.IDKATIOS  AND P.IdPrestamo=CYG.IDPRESTAMO
LEFT JOIN PNGeneral PNGCYG WITH(NOLOCK) ON PNGCYG.IDKATIOS=CYG.IDKATIOS AND PNGCYG.TDoc=CYG.TDOC AND PNGCYG.NDOC=CYG.NDOC
LEFT JOIN Personas PERCYG WITH(NOLOCK) ON PERCYG.IDKATIOS=CYG.IDKATIOS AND PERCYG.TDoc=CYG.TDOC AND PERCYG.NDOC=CYG.NDOC
LEFT JOIN @DIRECCIONES DIRCYG ON DIRCYG.IDKATIOS=CYG.IdKatios AND CYG.NDOC=DIRCYG.NDOC AND CYG.TDOC=DIRCYG.TDOC
WHERE P.IdKatios=@IDKATIOS 
AND P.IdEstado='ACTIVO'
AND P.PRODUCTO NOT IN ('Venta Cuota Creciente','Venta de Flujos')

IF OBJECT_ID('tempdb..#MAESTROCLIENTESTEMPORAL') IS NOT NULL  
   BEGIN  
    DROP TABLE #MAESTROCLIENTESTEMPORAL;
END
CREATE TABLE #MAESTROCLIENTESTEMPORAL
(	
CREDITO	VARCHAR(MAX)	
,TDOCUMENTO_TITULAR	VARCHAR(MAX)	
,NDOCUMENTO_TITULAR	VARCHAR(MAX)	
,NOMBRES_TITULAR	VARCHAR(MAX)	
,APELLIDOS_TITULAR	VARCHAR(MAX)	
,CELULAR_TITULAR	VARCHAR(MAX)	
,EMAIL_TITULAR	VARCHAR(MAX)	
,TELEFONO_TITULAR	VARCHAR(MAX)	
,DIRECCION_TITULAR	VARCHAR(MAX)	
,BARRIO_TITULAR	VARCHAR(MAX)	
,CIUDAD_TITULAR	VARCHAR(MAX)
,DEPARTAMENTO_TITULAR	VARCHAR(MAX)	
,TDOCUMENTO_SOLIDARIO	VARCHAR(MAX)	
,NDOCUMENTO_SOLIDARIO	VARCHAR(MAX)	
,NOMBRES_SOLIDARIO	VARCHAR(MAX)	
,APELLIDOS_SOLIDARIO	VARCHAR(MAX)	
,CELULAR_SOLIDARIO	VARCHAR(MAX)	
,EMAIL_SOLIDARIO	VARCHAR(MAX)	
,TELEFONO_SOLIDARIO	VARCHAR(MAX)	
,DIRECCION_SOLIDARIO	VARCHAR(MAX)	
,BARRIO_SOLIDARIO	VARCHAR(MAX)	
,CIUDAD_SOLIDARIO	VARCHAR(MAX)	
,DEPARTAMENTO_SOLIDARIO	VARCHAR(MAX)	
,TDOCUMENTO_CODEUDOR	VARCHAR(MAX)	
,NDOCUMENTO_CODEUDOR	VARCHAR(MAX)	
,NOMBRES_CODEUDOR	VARCHAR(MAX)	
,APELLIDOS_CODEUDOR	VARCHAR(MAX)	
,CELULAR_CODEUDOR	VARCHAR(MAX)	
,EMAIL_CODEUDOR	VARCHAR(MAX)	
,TELEFONO_CODEUDOR	VARCHAR(MAX)	
,DIRECCION_CODEUDOR	VARCHAR(MAX)	
,BARRIO_CODEUDOR	VARCHAR(MAX)	
,CIUDAD_CODEUDOR	VARCHAR(MAX)	
,DEPARTAMENTO_CODEUDOR	VARCHAR(MAX)
,TDOCUMENTO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,NDOCUMENTO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,NOMBRES_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,APELLIDOS_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,CELULAR_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,EMAIL_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,TELEFONO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,DIRECCION_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,BARRIO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,CIUDAD_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,TDOCUMENTO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,NDOCUMENTO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,NOMBRES_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,APELLIDOS_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,CELULAR_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,EMAIL_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,TELEFONO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,DIRECCION_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,BARRIO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,CIUDAD_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,TDOCUMENTO_CONYUGE	VARCHAR(MAX)	
,NDOCUMENTO_CONYUGE	VARCHAR(MAX)	
,NOMBRES_CONYUGE	VARCHAR(MAX)	
,APELLIDOS_CONYUGE	VARCHAR(MAX)	
,CELULAR_CONYUGE	VARCHAR(MAX)	
,EMAIL_CONYUGE	VARCHAR(MAX)	
,TELEFONO_CONYUGE	VARCHAR(MAX)	
,DIRECCION_CONYUGE	VARCHAR(MAX)	
,BARRIO_CONYUGE	VARCHAR(MAX)	
,CIUDAD_CONYUGE	VARCHAR(MAX)
,FNACIMIENTO VARCHAR(MAX)
,FECHA_NACIMIENTO_DEUDORES_SOLIDARIOS  VARCHAR(MAX)
,FECHA_NACIMIENTO_CODEUDORES  VARCHAR(MAX)
)

INSERT INTO #MAESTROCLIENTESTEMPORAL
SELECT 
TBLG.CREDITO
---Datos Titular
,TBLG.TDOCUMENTO TDOCUMENTO_TITULAR
,TBLG.NDOCUMENTO NDOCUMENTO_TITULAR
,TBLG.NOMBRES NOMBRES_TITULAR
,TBLG.APELLIDOS APELLIDOS_TITULAR
,TBLG.CELULAR CELULAR_TITULAR
,TBLG.EMAIL EMAIL_TITULAR
,ISNULL(TBLG.TELEFONO,'') TELEFONO_TITULAR
,ISNULL(TBLG.DIRECCION,'') DIRECCION_TITULAR
,ISNULL(TBLG.BARRIO,'') BARRIO_TITULAR
,ISNULL(TBLG.CIUDAD,'') CIUDAD_TITULAR
,ISNULL(TBLG.DEPARTAMENTO,'') DEPARTAMENTO_TITULAR
--Datos Solidario
,ISNULL(TBLGSOL.TDOCUMENTO ,'') TDOCUMENTO_SOLIDARIO
,ISNULL(TBLGSOL.NDOCUMENTO ,'') NDOCUMENTO_SOLIDARIO
,ISNULL(TBLGSOL.NOMBRES ,'') NOMBRES_SOLIDARIO
,ISNULL(TBLGSOL.APELLIDOS ,'') APELLIDOS_SOLIDARIO
,ISNULL(TBLGSOL.CELULAR ,'') CELULAR_SOLIDARIO
,ISNULL(TBLGSOL.EMAIL ,'') EMAIL_SOLIDARIO
,ISNULL(TBLGSOL.TELEFONO ,'') TELEFONO_SOLIDARIO
,ISNULL(TBLGSOL.DIRECCION ,'') DIRECCION_SOLIDARIO
,ISNULL(TBLGSOL.BARRIO ,'') BARRIO_SOLIDARIO
,ISNULL(TBLGSOL.CIUDAD ,'') CIUDAD_SOLIDARIO
,ISNULL(TBLGSOL.DEPARTAMENTO ,'') DEPARTAMENTO_SOLIDARIO
--Datos Codeudor
,ISNULL(TBLGCOD.TDOCUMENTO ,'') TDOCUMENTO_CODEUDOR
,ISNULL(TBLGCOD.NDOCUMENTO ,'') NDOCUMENTO_CODEUDOR
,ISNULL(TBLGCOD.NOMBRES ,'') NOMBRES_CODEUDOR
,ISNULL(TBLGCOD.APELLIDOS ,'') APELLIDOS_CODEUDOR
,ISNULL(TBLGCOD.CELULAR ,'') CELULAR_CODEUDOR
,ISNULL(TBLGCOD.EMAIL ,'') EMAIL_CODEUDOR
,ISNULL(TBLGCOD.TELEFONO ,'') TELEFONO_CODEUDOR
,ISNULL(TBLGCOD.DIRECCION ,'') DIRECCION_CODEUDOR
,ISNULL(TBLGCOD.BARRIO ,'') BARRIO_CODEUDOR
,ISNULL(TBLGCOD.CIUDAD ,'') CIUDAD_CODEUDOR
,ISNULL(TBLGCOD.DEPARTAMENTO ,'') DEPARTAMENTO_CODEUDOR
--Datos referencia-familiar
,ISNULL(TBLGREFFAM.TDOCUMENTO ,'') TDOCUMENTO_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.NDOCUMENTO ,'') NDOCUMENTO_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.NOMBRES ,'') NOMBRES_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.APELLIDOS ,'') APELLIDOS_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.CELULAR ,'') CELULAR_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.EMAIL ,'') EMAIL_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.TELEFONO ,'') TELEFONO_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.DIRECCION ,'') DIRECCION_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.BARRIO ,'') BARRIO_REFERENCIA_FAMILIAR
,ISNULL(TBLGREFFAM.CIUDAD ,'') CIUDAD_REFERENCIA_FAMILIAR
--Datos referencia-personal
,ISNULL(TBLGREFPER.TDOCUMENTO ,'') TDOCUMENTO_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.NDOCUMENTO ,'') NDOCUMENTO_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.NOMBRES ,'') NOMBRES_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.APELLIDOS ,'') APELLIDOS_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.CELULAR ,'') CELULAR_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.EMAIL  ,'') EMAIL_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.TELEFONO  ,'') TELEFONO_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.DIRECCION  ,'') DIRECCION_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.BARRIO  ,'') BARRIO_REFERENCIA_PERSONAL
,ISNULL(TBLGREFPER.CIUDAD  ,'')  CIUDAD_REFERENCIA_PERSONAL
--Datos Conyuge
,ISNULL(TBLGCYG.TDOCUMENTO  ,'') TDOCUMENTO_CONYUGE
,ISNULL(TBLGCYG.NDOCUMENTO  ,'') NDOCUMENTO_CONYUGE
,ISNULL(TBLGCYG.NOMBRES  ,'') NOMBRES_CONYUGE
,ISNULL(TBLGCYG.APELLIDOS  ,'') APELLIDOS_CONYUGE
,ISNULL(TBLGCYG.CELULAR  ,'') CELULAR_CONYUGE
,ISNULL(TBLGCYG.EMAIL  ,'') EMAIL_CONYUGE
,ISNULL(TBLGCYG.TELEFONO  ,'') TELEFONO_CONYUGE
,ISNULL(TBLGCYG.DIRECCION  ,'') DIRECCION_CONYUGE
,ISNULL(TBLGCYG.BARRIO  ,'') BARRIO_CONYUGE
,ISNULL(TBLGCYG.CIUDAD  ,'') CIUDAD_CONYUGE
--FECHA DE NACIMIENTO
,ISNULL(TBLG.PERFechaNacimiento  ,'') FECHA_NACIMIENTO_TITULAR
,ISNULL(TBLGSOL.PERFechaNacimiento  ,'') FECHA_NACIMIENTO_DEUDORES_SOLIDARIOS
,ISNULL(TBLGCOD.PERFechaNacimiento  ,'') FECHA_NACIMIENTO_CODEUDORES

FROM @TABLAGENERAL TBLG 
LEFT JOIN @TABLAGENERAL TBLGSOL ON TBLG.CREDITO=TBLGSOL.CREDITO AND TBLGSOL.TIPO='Solidario'
LEFT JOIN @TABLAGENERAL TBLGCOD ON TBLG.CREDITO=TBLGCOD.CREDITO AND TBLGCOD.TIPO='Codeudor'
LEFT JOIN @TABLAGENERAL TBLGREFFAM ON TBLG.CREDITO=TBLGREFFAM.CREDITO AND TBLGREFFAM.TIPO='Familiar'
LEFT JOIN @TABLAGENERAL TBLGREFPER ON TBLG.CREDITO=TBLGREFPER.CREDITO AND TBLGREFPER.TIPO='Personal'
LEFT JOIN @TABLAGENERAL TBLGCYG ON TBLG.CREDITO=TBLGCYG.CREDITO AND TBLGCYG.TIPO='Conyuge'
WHERE TBLG.TIPO='Titular'

END 

USE K003_2
CREATE TABLE MAESTROCLIENTES
(	
CREDITO	VARCHAR(MAX)	
,TDOCUMENTO_TITULAR	VARCHAR(MAX)	
,NDOCUMENTO_TITULAR	VARCHAR(MAX)	
,NOMBRES_TITULAR	VARCHAR(MAX)	
,APELLIDOS_TITULAR	VARCHAR(MAX)	
,CELULAR_TITULAR	VARCHAR(MAX)	
,EMAIL_TITULAR	VARCHAR(MAX)	
,TELEFONO_TITULAR	VARCHAR(MAX)	
,DIRECCION_TITULAR	VARCHAR(MAX)	
,BARRIO_TITULAR	VARCHAR(MAX)	
,CIUDAD_TITULAR	VARCHAR(MAX)
,DEPARTAMENTO_TITULAR	VARCHAR(MAX)	
,TDOCUMENTO_SOLIDARIO	VARCHAR(MAX)	
,NDOCUMENTO_SOLIDARIO	VARCHAR(MAX)	
,NOMBRES_SOLIDARIO	VARCHAR(MAX)	
,APELLIDOS_SOLIDARIO	VARCHAR(MAX)	
,CELULAR_SOLIDARIO	VARCHAR(MAX)	
,EMAIL_SOLIDARIO	VARCHAR(MAX)	
,TELEFONO_SOLIDARIO	VARCHAR(MAX)	
,DIRECCION_SOLIDARIO	VARCHAR(MAX)	
,BARRIO_SOLIDARIO	VARCHAR(MAX)	
,CIUDAD_SOLIDARIO	VARCHAR(MAX)	
,DEPARTAMENTO_SOLIDARIO	VARCHAR(MAX)	
,TDOCUMENTO_CODEUDOR	VARCHAR(MAX)	
,NDOCUMENTO_CODEUDOR	VARCHAR(MAX)	
,NOMBRES_CODEUDOR	VARCHAR(MAX)	
,APELLIDOS_CODEUDOR	VARCHAR(MAX)	
,CELULAR_CODEUDOR	VARCHAR(MAX)	
,EMAIL_CODEUDOR	VARCHAR(MAX)	
,TELEFONO_CODEUDOR	VARCHAR(MAX)	
,DIRECCION_CODEUDOR	VARCHAR(MAX)	
,BARRIO_CODEUDOR	VARCHAR(MAX)	
,CIUDAD_CODEUDOR	VARCHAR(MAX)	
,DEPARTAMENTO_CODEUDOR	VARCHAR(MAX)
,TDOCUMENTO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,NDOCUMENTO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,NOMBRES_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,APELLIDOS_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,CELULAR_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,EMAIL_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,TELEFONO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,DIRECCION_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,BARRIO_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,CIUDAD_REFERENCIA_FAMILIAR	VARCHAR(MAX)	
,TDOCUMENTO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,NDOCUMENTO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,NOMBRES_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,APELLIDOS_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,CELULAR_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,EMAIL_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,TELEFONO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,DIRECCION_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,BARRIO_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,CIUDAD_REFERENCIA_PERSONAL	VARCHAR(MAX)	
,TDOCUMENTO_CONYUGE	VARCHAR(MAX)	
,NDOCUMENTO_CONYUGE	VARCHAR(MAX)	
,NOMBRES_CONYUGE	VARCHAR(MAX)	
,APELLIDOS_CONYUGE	VARCHAR(MAX)	
,CELULAR_CONYUGE	VARCHAR(MAX)	
,EMAIL_CONYUGE	VARCHAR(MAX)	
,TELEFONO_CONYUGE	VARCHAR(MAX)	
,DIRECCION_CONYUGE	VARCHAR(MAX)	
,BARRIO_CONYUGE	VARCHAR(MAX)	
,CIUDAD_CONYUGE	VARCHAR(MAX)
,FNACIMIENTO VARCHAR(MAX)
,FECHA_NACIMIENTO_DEUDORES_SOLIDARIOS  VARCHAR(MAX)
,FECHA_NACIMIENTO_CODEUDORES  VARCHAR(MAX)
)

INSERT INTO MAESTROCLIENTES
SELECT
M.CREDITO,
M.TDOCUMENTO_TITULAR,
M.NDOCUMENTO_TITULAR,
M.NOMBRES_TITULAR,
M.APELLIDOS_TITULAR,
M.CELULAR_TITULAR,
M.EMAIL_TITULAR,
M.TELEFONO_TITULAR,
M.DIRECCION_TITULAR,
M.BARRIO_TITULAR,
M.CIUDAD_TITULAR,
M.DEPARTAMENTO_TITULAR,
M.TDOCUMENTO_SOLIDARIO,
M.NDOCUMENTO_SOLIDARIO,
M.NOMBRES_SOLIDARIO,
M.APELLIDOS_SOLIDARIO,
M.CELULAR_SOLIDARIO,
M.EMAIL_SOLIDARIO,
M.TELEFONO_SOLIDARIO,
M.DIRECCION_SOLIDARIO,
M.BARRIO_SOLIDARIO,
M.CIUDAD_SOLIDARIO,
M.DEPARTAMENTO_SOLIDARIO,
M.TDOCUMENTO_CODEUDOR,
M.NDOCUMENTO_CODEUDOR,
M.NOMBRES_CODEUDOR,
M.APELLIDOS_CODEUDOR,
M.CELULAR_CODEUDOR,
M.EMAIL_CODEUDOR,
M.TELEFONO_CODEUDOR,
M.DIRECCION_CODEUDOR,
M.BARRIO_CODEUDOR,
M.CIUDAD_CODEUDOR,
M.DEPARTAMENTO_CODEUDOR,
M.TDOCUMENTO_REFERENCIA_FAMILIAR,
M.NDOCUMENTO_REFERENCIA_FAMILIAR,
M.NOMBRES_REFERENCIA_FAMILIAR,
M.APELLIDOS_REFERENCIA_FAMILIAR,
M.CELULAR_REFERENCIA_FAMILIAR,
M.EMAIL_REFERENCIA_FAMILIAR,
M.TELEFONO_REFERENCIA_FAMILIAR,
M.DIRECCION_REFERENCIA_FAMILIAR,
M.BARRIO_REFERENCIA_FAMILIAR,
M.CIUDAD_REFERENCIA_FAMILIAR,
M.TDOCUMENTO_REFERENCIA_PERSONAL,
M.NDOCUMENTO_REFERENCIA_PERSONAL,
M.NOMBRES_REFERENCIA_PERSONAL,
M.APELLIDOS_REFERENCIA_PERSONAL,
M.CELULAR_REFERENCIA_PERSONAL,
M.EMAIL_REFERENCIA_PERSONAL,
M.TELEFONO_REFERENCIA_PERSONAL,
M.DIRECCION_REFERENCIA_PERSONAL,
M.BARRIO_REFERENCIA_PERSONAL,
M.CIUDAD_REFERENCIA_PERSONAL,
M.TDOCUMENTO_CONYUGE,
M.NDOCUMENTO_CONYUGE,
M.NOMBRES_CONYUGE,
M.APELLIDOS_CONYUGE,
M.CELULAR_CONYUGE,
M.EMAIL_CONYUGE,
M.TELEFONO_CONYUGE,
M.DIRECCION_CONYUGE,
M.BARRIO_CONYUGE,
M.CIUDAD_CONYUGE,
M.FNACIMIENTO,
M.FECHA_NACIMIENTO_DEUDORES_SOLIDARIOS,
M.FECHA_NACIMIENTO_CODEUDORES
FROM #MAESTROCLIENTESTEMPORAL M
