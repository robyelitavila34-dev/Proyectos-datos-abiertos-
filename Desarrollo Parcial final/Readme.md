# Mapa de calor de turismo — Final Copa Sudamericana 2026 en Barranquilla

Aplicación web (Python + Flask + PostgreSQL, patrón MVC) que:

1. consulta una API de datos.gov.co (Socrata/SODA),
2. guarda los registros en PostgreSQL sin duplicar,
3. muestra un **mapa de calor** (Leaflet) con las zonas de mayor concentración turística,
4. marca el **Estadio Metropolitano Roberto Meléndez** (sede de Atlético Mineiro vs Boca Juniors, 21 de noviembre de 2026) y permite filtrar lo que está a X km del estadio,
5. ofrece búsqueda por texto, municipio y categoría, con un resumen numérico.

## Lenguajes y tecnologías (y para qué sirve cada una)

| Tecnología | Para qué se usa aquí |
|---|---|
| **Python** | Lógica de la aplicación (consumir la API, hablar con la base de datos) |
| **Flask** | Servidor web: recibe lo que pide el navegador y responde (las "rutas") |
| **API REST / JSON** | Forma en que datos.gov.co entrega los datos |
| **SQL (PostgreSQL)** | Guardar los datos y hacer las consultas (filtros, conteos, distancias) |
| **HTML / CSS** | Lo que se ve en el navegador (página, tabla, estilos) |
| **JavaScript (Leaflet)** | Dibujar el mapa. Es un archivo dentro de la plantilla; no hay que programarlo desde cero |

## Elegir el dataset (paso obligatorio)

El mapa necesita registros **con coordenadas** (latitud/longitud).

- Recomendado: [Atractivos o Productos Turísticos del departamento del Atlántico](https://www.datos.gov.co/Comercio-Industria-y-Turismo/Atractivos-o-Productos-Tur-sticos-del-departamento/2fsd-7enq), ID `2fsd-7enq` (ya viene en `.env.example`).
- Alternativa para otras ciudades: [RNT de Cartagena](https://www.datos.gov.co/Comercio-Industria-y-Turismo/Registro-Nacional-de-Turismo-RNT-de-Cartagena/bn6d-kasp), ID `bn6d-kasp`.

> Los nombres de columnas de estos datasets **no se pudieron verificar** al preparar el proyecto.
> Ejecuta `python probar_api.py`: imprime los campos reales y cómo se normalizan. Si `latitud`/`longitud`
> salen en `None`, escribe el nombre exacto del campo en `CAMPO_LATITUD` y `CAMPO_LONGITUD` del `.env`.
> Si el dataset no trae coordenadas, busca otro en https://www.datos.gov.co ("turismo" + revisar que tenga latitud/longitud).

Anota en este README el dataset final: nombre, entidad, propósito y enlace.

## Estructura MVC

| Archivo | Rol |
|---|---|
| `models/datos_model.py` | **Modelo**: conexión a PostgreSQL, inserción sin duplicados, consultas SELECT y agregaciones |
| `templates/index.html` | **Vista**: formulario, tarjetas, tabla y mapa (solo pide JSON al controlador) |
| `app.py` | **Controlador**: rutas `/`, `/sincronizar` (POST) y `/api/puntos` (JSON del mapa) |
| `api/api_client.py` | **Servicio**: consume la API y normaliza los campos |
| `config.py` | Configuración: coordenadas del estadio |

La vista nunca toca la base de datos; el modelo nunca genera HTML.

## Cómo conectarlo con PostgreSQL (paso a paso)

**1. Instalar PostgreSQL** desde https://www.postgresql.org/download/windows/ (incluye pgAdmin). Durante la instalación
define una contraseña para el usuario `postgres` (guárdala) y deja el puerto `5432`.

**2. Crear la base y la tabla.** Abre **pgAdmin**:
- Clic derecho en *Databases → Create → Database…* y nómbrala `turismo_mapa`.
- Clic derecho en `turismo_mapa` → *Query Tool*. Pega el **PASO 2** de `sql/crear_bd_postgres.sql` (desde `CREATE TABLE` hasta los `CREATE INDEX`) y ejecútalo (botón ▶).

**3. Crear el archivo `.env`** copiando `.env.example` y editando estas líneas:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turismo_mapa
DB_USER=postgres
DB_PASSWORD=la_contraseña_que_pusiste
API_RESOURCE_ID=2fsd-7enq
```

Así la contraseña no queda escrita en el código. **No subas `.env` a GitHub ni lo compartas.**

**4. Instalar y ejecutar** (en PowerShell, dentro de la carpeta del proyecto):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python probar_api.py      # revisa que la API responda y que se vean latitud y longitud
python app.py
```

**5. Abrir** http://127.0.0.1:5000, pulsar **Consultar API y guardar datos** y verificar en pgAdmin:
`SELECT * FROM registros_turismo;`. Pulsar el botón de nuevo no duplica registros.

### Si algo falla

| Error | Qué revisar |
|---|---|
| `password authentication failed` | `DB_USER` y `DB_PASSWORD` en `.env` |
| `connection refused` / `could not connect` | Que el servicio PostgreSQL esté iniciado y que `DB_PORT` sea el de la instalación |
| `database "turismo_mapa" does not exist` | Crear la base (paso 2) |
| `relation "registros_turismo" does not exist` | Ejecutar el CREATE TABLE en la base correcta |
| `ModuleNotFoundError` | Activar el entorno virtual y `pip install -r requirements.txt` |
| HTTP 404 de la API | Revisar `API_RESOURCE_ID` |
| Mapa vacío con registros guardados | Los registros no traen coordenadas: ajustar `CAMPO_LATITUD` / `CAMPO_LONGITUD` |

## Cómo se calcula el mapa de calor

`puntos_mapa()` agrupa los registros en celdas de ~100 m (`ROUND(lat,3)`, `ROUND(lon,3)`) y cuenta cuántos caen en cada una.
Ese conteo es la **frecuencia**; el mapa la dibuja de azul (poco) a rojo (mucho). Los filtros (texto, municipio, categoría, radio)
se aplican también al mapa.

## Distancia al estadio

La distancia en km se calcula en SQL con la fórmula de Haversine (sin extensiones). Las coordenadas del estadio
(10.926861, -74.800722) vienen de Wikipedia y son aproximadas: verifícalas y ajústalas en `.env` si hace falta.

## Consultas de ejemplo

Están comentadas al final de `sql/crear_bd_postgres.sql` (zonas con más registros, por municipio, por categoría y los más
cercanos al estadio).

## Clave alternativa si la API no trae identificador

Si el registro no tiene id, se usa un hash SHA-1 del contenido como `id_api`. Debe explicarse en la sustentación.

## Seguridad

No subir `.env`; consultas parametrizadas (`%s`); `debug=True` solo en local.
