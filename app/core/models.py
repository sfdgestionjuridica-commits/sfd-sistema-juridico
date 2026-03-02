from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from .database import Base

# 👤 CLIENTE
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    cedula = Column(String)
    telefono = Column(String)
    email = Column(String)


# ⚖️ CASO (NÚCLEO)
class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    radicado = Column(String)
    tipo_proceso = Column(String)
    descripcion = Column(String)
    estado = Column(String, default="captacion")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)


# 📍 HITOS (SEGUIMIENTO)
class Hito(Base):
    __tablename__ = "hitos"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    descripcion = Column(String)
    estado = Column(String)  # pendiente / completado
    fecha = Column(DateTime, default=datetime.utcnow)