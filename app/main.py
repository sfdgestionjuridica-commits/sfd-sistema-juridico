import streamlit as st
from core.database import engine, Base
from modules.captacion.formulario1 import formulario_1

from modules.captacion.service import inicializar_db

import threading
from modules.seguimiento.scheduler import iniciar_scheduler

# 🔥 INICIALIZAR DB SIEMPRE
inicializar_db()

# 🔥 INICIAR BOT (SOLO UNA VEZ)
if "bot_iniciado" not in st.session_state:
    threading.Thread(target=iniciar_scheduler, daemon=True).start()
    st.session_state["bot_iniciado"] = True
    print("✅ BOT inicializado")  # 👈 SOLO CONSOLA

# Crear tablas
Base.metadata.create_all(bind=engine)

formulario_1()