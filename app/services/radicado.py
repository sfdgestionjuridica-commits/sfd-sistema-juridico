import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema.db")


def generar_radicado(rol: str) -> str:
    """
    Radicado con consecutivo GLOBAL real basado en tabla casos
    """

    mapa = {
        "1": "DTE",
        "2": "DTE-S",
        "3": "DDO",
        "4": "DDO-S",
        "5": "TRA"
    }

    sigla = mapa.get(rol, "GEN")
    anio = datetime.now().year

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔥 CLAVE: TOMAR EL ÚLTIMO REGISTRO REAL
    cursor.execute("""
        SELECT radicado FROM casos
        ORDER BY id DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()

    if resultado:
        ultimo = resultado[0]
        try:
            consecutivo = int(ultimo.split("-")[-1]) + 1
        except:
            consecutivo = 1
    else:
        consecutivo = 1

    conn.close()

    consecutivo_str = str(consecutivo).zfill(5)

    return f"SFD-{anio}-{sigla}-{consecutivo_str}"