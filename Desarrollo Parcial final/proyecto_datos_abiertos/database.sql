CREATE DATABASE DatosAbiertosDB;
GO

USE DatosAbiertosDB;
GO

CREATE TABLE RegistrosAPI (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_api NVARCHAR(100) NOT NULL UNIQUE,
    municipio NVARCHAR(150) NULL,
    tipo_de_atractivo NVARCHAR(150) NULL,
    nombre_atractivo NVARCHAR(250) NULL,
    lugar_ubicacion NVARCHAR(250) NULL,
    descripcion NVARCHAR(MAX) NULL,
    json_original NVARCHAR(MAX) NULL,
    fecha_captura DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO
