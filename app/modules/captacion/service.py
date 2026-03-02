import sqlite3
import datetime

DB_PATH = "sistema.db"


# ================================
# 🔥 CONEXIÓN SEGURA
# ================================
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ================================
# 🔥 INICIALIZAR TODAS LAS TABLAS
# ================================
def inicializar_db():

    conn = get_connection()
    cursor = conn.cursor()

    # Tabla casos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radicado TEXT,
            nombre TEXT,
            cedula TEXT,
            telefono TEXT,
            whatsapp TEXT,
            email TEXT,
            direccion TEXT,
            empresa TEXT,
            rol TEXT,
            descripcion TEXT,
            fecha TEXT
        )
    """)

    # Tabla consecutivos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consecutivos (
            sigla TEXT PRIMARY KEY,
            valor INTEGER
        )
    """)

    # Tabla procesos (BOT)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radicado TEXT UNIQUE,
            estado_actual TEXT
        )
    """)

    conn.commit()
    conn.close()


# ================================
# 🔥 GENERAR RADICADO
# ================================
def generar_radicado(rol: str) -> str:

    mapa = {
        "1": "DTE",
        "2": "DTE-S",
        "3": "DDO",
        "4": "DDO-S",
        "5": "TRA"
    }

    sigla = mapa.get(rol, "GEN")
    anio = datetime.datetime.now().year

    conn = get_connection()
    cursor = conn.cursor()

    # Inicializar sigla
    cursor.execute("""
        INSERT OR IGNORE INTO consecutivos (sigla, valor)
        VALUES (?, 0)
    """, (sigla,))

    cursor.execute("""
        SELECT valor FROM consecutivos WHERE sigla = ?
    """, (sigla,))

    actual = cursor.fetchone()[0]
    nuevo = actual + 1

    cursor.execute("""
        UPDATE consecutivos
        SET valor = ?
        WHERE sigla = ?
    """, (nuevo, sigla))

    conn.commit()
    conn.close()

    consecutivo = str(nuevo).zfill(5)

    return f"SFD-{anio}-{sigla}-{consecutivo}"


# ================================
# 🔥 CREAR CASO (TODO INTEGRADO)
# ================================
def crear_caso(data: dict) -> str:

    # 1. Inicializar DB (garantiza todo)
    inicializar_db()

    rol = data.get("rol")

    # 2. Generar radicado
    radicado = data["radicado"]

    conn = get_connection()
    cursor = conn.cursor()

    # 3. Guardar caso
    cursor.execute("""
        INSERT INTO casos (
            radicado, nombre, cedula, telefono,
            whatsapp, email, direccion, empresa,
            rol, descripcion, fecha
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        radicado,
        data.get("nombre"),
        data.get("cedula"),
        data.get("telefono"),
        data.get("whatsapp"),
        data.get("email"),
        data.get("direccion"),
        data.get("empresa"),
        rol,
        data.get("descripcion"),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    # 4. Registrar en procesos (BOT)
    cursor.execute("""
        INSERT OR IGNORE INTO procesos (radicado, estado_actual)
        VALUES (?, ?)
    """, (radicado, "SIN CAMBIOS"))

    conn.commit()
    conn.close()

    return radicado