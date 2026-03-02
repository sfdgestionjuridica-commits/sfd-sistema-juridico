from modules.seguimiento.scraper import consultar_estado
from modules.seguimiento.service import (
    obtener_procesos_activos,
    guardar_actualizacion
)

def ejecutar_bot():

    print("🤖 Ejecutando BOT de seguimiento...")

    procesos = obtener_procesos_activos()

    for proceso in procesos:

        estado_nuevo = consultar_estado(proceso["radicado"])

        if estado_nuevo != proceso["estado_actual"]:

            guardar_actualizacion(proceso["id"], estado_nuevo)

            print(f"🔔 Cambio detectado en {proceso['radicado']}")