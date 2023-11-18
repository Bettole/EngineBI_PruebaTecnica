--- Creacion tablas
IF object_id('DimPeriodos') IS NOT NULL
	DROP TABLE DimPeriodos

CREATE TABLE DimPeriodos (
	PeriodoID INT PRIMARY KEY
	,Trimestre VARCHAR(10)
	);

IF object_id('DimForecasts') IS NOT NULL
	DROP TABLE DimForecasts

CREATE TABLE DimForecasts (
	ForecastID INT PRIMARY KEY
	,Forecast VARCHAR(20)
	);

IF object_id('FactRealIngresado') IS NOT NULL
	DROP TABLE FactRealIngresado

CREATE TABLE FactRealIngresado (
	ID INT IDENTITY(1, 1)
	,ValorRealIngresado FLOAT
	,PeriodoID INT
	,ForecastID INT
	,FOREIGN KEY (PeriodoID) REFERENCES DimPeriodos(PeriodoID)
	,FOREIGN KEY (ForecastID) REFERENCES DimForecasts(ForecastID)
	);

--- Poblacion de tablas
INSERT INTO DimForecasts (
	ForecastID
	,Forecast
	)
VALUES 
    (1, 'Forecast1'),
    (2, 'Forecast2'),
    (3, 'Forecast3'),
    (4, 'Forecast4')

--- Recomendación: poblar esta dimensión con todos los periodos de los siguientes meses para los proximos años
INSERT INTO DimPeriodos (
	PeriodoID
	,Trimestre
	)
VALUES 
	(202301, 'Q1')
	,(202302, 'Q1')
	,(202303, 'Q1')
	,(202304, 'Q2')
	,(202305, 'Q2')
	,(202306, 'Q2')
	,(202307, 'Q3')
	,(202308, 'Q3')
	,(202309, 'Q3')
	,(202310, 'Q4')
	,(202311, 'Q4')
	,(202312, 'Q4')

	,(202401, 'Q1')
	,(202402, 'Q1')
	,(202403, 'Q1') 
	,(202404, 'Q1')
	,(202405, 'Q1')
	,(202406, 'Q1')


TRUNCATE TABLE FactRealIngresado

INSERT INTO FactRealIngresado (
	ValorRealIngresado
	,PeriodoID
	,ForecastID
	)
VALUES
    (100, 202301, 1),
    (120, 202302, 1),
    (130, 202303, 1),

    (140, 202304, 2),
    (150, 202305, 2),
    (160, 202306, 2),

    (170, 202307, 3),
    (180, 202308, 3),
    (190, 202309, 3),

    (200, 202310, 4),
    (210, 202311, 4),
    (220, 202312, 4),

    (400, 202401, 1),
    (410, 202402, 1),
    (420, 202403, 1) ,

    (430, 202404, 2),
    (440, 202405, 2),
    (450, 202406, 2) 

--- Consulta Forecast
SELECT f.ID
	,f.ValorRealIngresado
	,left(t.PeriodoID, 4) Anio
	,t.Trimestre
	,right(t.PeriodoID, 2) Mes
	,d.Forecast
FROM FactRealIngresado f
INNER JOIN DimPeriodos t ON f.PeriodoID = t.PeriodoID
INNER JOIN DimForecasts d ON d.ForecastID >= f.ForecastID