import os
import json
import hashlib
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def obtener_conexion():
    servidor = os.getenv("DB_SERVER")
    base_datos = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted = os.getenv("DB_TRUSTED", "yes").strip().lower()

    if trusted == "yes":
        cadena = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor};"
            f"DATABASE={base_datos};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        usuario = os.getenv("DB_USER")
        clave = os.getenv("DB_PASSWORD")
        cadena = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor};"
            f"DATABASE={base_datos};"
            f"UID={usuario};"
            f"PWD={clave};"
            "TrustServerCertificate=yes;"
        )

    return pyodbc.connect(cadena)


def _extraer_campos(registro):
    municipio = str(registro.get("municipio") or "").strip()
    tipo_atractivo = str(
        registro.get("tipo_de_atractivo")
        or registro.get("tipo_atractivo")
        or ""
    ).strip()
    nombre_atractivo = str(
        registro.get("nombre_del_atractivo")
        or registro.get("nombre_atractivo")
        or registro.get("nombre")
        or registro.get("atractivo")
        or ""
    ).strip()
    lugar_ubicacion = str(
        registro.get("lugar_de_ubicacion")
        or registro.get("lugar_ubicacion")
        or registro.get("ubicacion")
        or ""
    ).strip()
    descripcion = str(registro.get("descripcion") or "").strip()

    identificador = str(
        registro.get("id")
        or registro.get("codigo")
        or registro.get(":id")
        or ""
    ).strip()

    if not identificador:
        clave_base = f"{municipio}|{tipo_atractivo}|{nombre_atractivo}|{lugar_ubicacion}"
        identificador = hashlib.sha256(clave_base.encode("utf-8")).hexdigest()[:32]

    return {
        "id_api": identificador,
        "municipio": municipio,
        "tipo_de_atractivo": tipo_atractivo,
        "nombre_atractivo": nombre_atractivo,
        "lugar_ubicacion": lugar_ubicacion,
        "descripcion": descripcion,
    }


def guardar_registros(registros):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    insertados = 0

    try:
        for registro in registros:
            datos = _extraer_campos(registro)
            if not datos["id_api"]:
                continue

            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1 FROM RegistrosAPI WHERE id_api = ?
                )
                INSERT INTO RegistrosAPI
                (id_api, municipio, tipo_de_atractivo, nombre_atractivo,
                 lugar_ubicacion, descripcion, json_original)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                datos["id_api"],
                datos["id_api"],
                datos["municipio"],
                datos["tipo_de_atractivo"],
                datos["nombre_atractivo"],
                datos["lugar_ubicacion"],
                datos["descripcion"],
                json.dumps(registro, ensure_ascii=False),
            )
            if cursor.rowcount > 0:
                insertados += 1

        conexion.commit()
        return insertados
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def consultar_registros(filtro=""):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        if filtro:
            patron = f"%{filtro}%"
            cursor.execute(
                """
                SELECT TOP 100 id_api, municipio, tipo_de_atractivo,
                       nombre_atractivo, lugar_ubicacion, descripcion
                FROM RegistrosAPI
                WHERE municipio LIKE ?
                   OR tipo_de_atractivo LIKE ?
                   OR nombre_atractivo LIKE ?
                ORDER BY id DESC
                """,
                patron,
                patron,
                patron,
            )
        else:
            cursor.execute(
                """
                SELECT TOP 100 id_api, municipio, tipo_de_atractivo,
                       nombre_atractivo, lugar_ubicacion, descripcion
                FROM RegistrosAPI
                ORDER BY id DESC
                """
            )

        columnas = [columna[0] for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def obtener_resumen_numerico():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_registros,
                COUNT(DISTINCT NULLIF(LTRIM(RTRIM(municipio)), '')) AS total_municipios,
                COUNT(DISTINCT NULLIF(LTRIM(RTRIM(tipo_de_atractivo)), '')) AS total_tipos
            FROM RegistrosAPI
            """
        )
        fila = cursor.fetchone()
        return {
            "total_registros": fila[0] if fila else 0,
            "total_municipios": fila[1] if fila else 0,
            "total_tipos": fila[2] if fila else 0,
        }
    finally:
        cursor.close()
        conexion.close()


def obtener_datos_mapa_calor():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                COALESCE(NULLIF(LTRIM(RTRIM(municipio)), ''), 'Sin municipio') AS municipio,
                COALESCE(NULLIF(LTRIM(RTRIM(tipo_de_atractivo)), ''), 'Sin tipo') AS tipo_de_atractivo,
                COUNT(*) AS frecuencia
            FROM RegistrosAPI
            GROUP BY
                COALESCE(NULLIF(LTRIM(RTRIM(municipio)), ''), 'Sin municipio'),
                COALESCE(NULLIF(LTRIM(RTRIM(tipo_de_atractivo)), ''), 'Sin tipo')
            ORDER BY municipio ASC, tipo_de_atractivo ASC
            """
        )
        filas = cursor.fetchall()

        municipios_set = set()
        tipos_set = set()
        conteos = {}
        max_frecuencia = 0

        for municipio, tipo, frecuencia in filas:
            municipios_set.add(municipio)
            tipos_set.add(tipo)
            conteos[(municipio, tipo)] = frecuencia
            if frecuencia > max_frecuencia:
                max_frecuencia = frecuencia

        municipios = sorted(municipios_set)
        tipos = sorted(tipos_set)

        matriz = {}
        totales_municipio = {}
        totales_tipo = {tipo: 0 for tipo in tipos}
        total_general = 0

        for municipio in municipios:
            matriz[municipio] = {}
            suma_fila = 0
            for tipo in tipos:
                valor = conteos.get((municipio, tipo), 0)
                matriz[municipio][tipo] = valor
                suma_fila += valor
                totales_tipo[tipo] += valor
                total_general += valor
            totales_municipio[municipio] = suma_fila

        return {
            "municipios": municipios,
            "tipos": tipos,
            "matriz": matriz,
            "totales_municipio": totales_municipio,
            "totales_tipo": totales_tipo,
            "max_frecuencia": max_frecuencia,
            "total_general": total_general,
        }
    finally:
        cursor.close()
        conexion.close()
