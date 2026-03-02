import schedule
import time
from modules.seguimiento.bot import ejecutar_bot

def iniciar_scheduler():

    print("🟢 Scheduler iniciado...")

    # Ejecutar cada 1 minuto (PRUEBA)
    schedule.every(1).minutes.do(ejecutar_bot)

    # 🔥 PRODUCCIÓN:
    # schedule.every().day.at("08:00").do(ejecutar_bot)

    while True:
        schedule.run_pending()
        time.sleep(5)