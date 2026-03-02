import sqlite3

DB_PATH = "sistema.db"


def obtener_procesos_activos():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla correctamente (SIN columna activo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radicado TEXT,
            estado_actual TEXT
        )
    """)

    cursor.execute("""
        SELECT id, radicado, estado_actual
        FROM procesos
    """)

    rows = cursor.fetchall()
    conn.close()

    procesos = []

    for row in rows:
        procesos.append({
            "id": row[0],
            "radicado": row[1],
            "estado_actual": row[2]
        })

    return procesos


def guardar_actualizacion(proceso_id, nuevo_estado):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE procesos
        SET estado_actual = ?
        WHERE id = ?
    """, (nuevo_estado, proceso_id))

    conn.commit()
    conn.close()