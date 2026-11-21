# Atractivos y Productos Turísticos del Atlántico

*Aplicación web desarrollada con Python, consumo de API, SQL Server y arquitectura MVC.*

## 1. Descripción del proyecto

El proyecto *Atractivos y Productos Turísticos del Atlántico* consiste en el desarrollo de una aplicación web que permite consultar, almacenar y visualizar información relacionada con los atractivos turísticos de los municipios del departamento del Atlántico.

Para su desarrollo utilizamos Python, Flask, una API pública de Datos Abiertos Colombia y Microsoft SQL Server. La aplicación obtiene información de una fuente externa, procesa los registros recibidos en formato JSON y los almacena en una base de datos para facilitar su consulta.

Además, cuenta con una interfaz web que permite buscar atractivos turísticos, visualizar registros, consultar estadísticas y analizar la frecuencia de los atractivos mediante un mapa de calor.

## 2. Justificación

Decidimos realizar este proyecto porque consideramos importante aprovechar la información pública relacionada con el turismo del departamento del Atlántico y facilitar su consulta mediante herramientas tecnológicas.

A través de esta aplicación buscamos organizar los datos turísticos en una base de datos y presentarlos de una manera sencilla y comprensible.

Asimismo, el proyecto nos permitió poner en práctica los conocimientos adquiridos durante la asignatura, especialmente en programación con Python, consumo de API, conexión con SQL Server y arquitectura MVC.

## 3. Objetivos

*Objetivo general*

Desarrollar una aplicación web que permita consultar, almacenar y visualizar información turística del departamento del Atlántico, integrando Python, una API pública, SQL Server y arquitectura MVC.

*Objetivos específicos*

- Consultar información turística mediante una API pública.
- Procesar y organizar los datos recibidos en formato JSON.
- Almacenar los registros en SQL Server.
- Evitar la duplicación de información.
- Implementar búsquedas de registros.
- Mostrar estadísticas y un mapa de calor.
- Organizar el código mediante la arquitectura MVC.

## 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Desarrollo de la lógica del sistema. |
| Flask | Creación y administración de la aplicación web. |
| Datos Abiertos Colombia | Fuente de información turística. |
| API REST | Obtención de los registros. |
| JSON | Formato de los datos recibidos. |
| SQL Server | Almacenamiento de la información. |
| SQL | Creación y consulta de la base de datos. |
| pyodbc | Conexión entre Python y SQL Server. |
| python-dotenv | Administración de variables de configuración. |
| HTML | Estructura de la interfaz. |
| CSS | Diseño visual de la aplicación. |
| Jinja2 | Presentación dinámica de los datos. |
| GitHub | Almacenamiento y publicación del proyecto. |

## 5. Fuente de información: API

Para obtener los datos utilizamos la plataforma *Datos Abiertos Colombia*, específicamente el conjunto de datos identificado con el código 2fsd-7enq.

La API proporciona información en formato JSON, que nuestra aplicación recibe y procesa mediante Python.

Entre los datos obtenidos se encuentran el municipio, tipo de atractivo, nombre, ubicación y descripción.

La consulta se realiza desde el módulo `api