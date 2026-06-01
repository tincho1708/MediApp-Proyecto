from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Especialidad(Base):
    __tablename__ = "especialidad"

    id_especialidad = Column(Integer, primary_key=True, index=True)
    nombre_especialidad = Column(String(100), nullable=False)

    medicos = relationship("Medico", back_populates="especialidad")


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20))
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    mail = Column(String(255), unique=True, nullable=False)
    especialidad_id = Column(Integer, ForeignKey("especialidad.id_especialidad"))
    password_hash = Column(String(255), nullable=False)
    email_verificado = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    especialidad = relationship("Especialidad", back_populates="medicos")
    turnos = relationship("Turno", back_populates="medico")
    resenas = relationship("Resena", back_populates="medico")
    recomendaciones_dadas = relationship("Recomienda", foreign_keys="Recomienda.id_medico", back_populates="medico")
    recomendaciones_recibidas = relationship("Recomienda", foreign_keys="Recomienda.id_medico_recomendado", back_populates="medico_recomendado")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    mail = Column(String(255), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    email_verificado = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    turnos = relationship("Turno", back_populates="paciente")
    resenas = relationship("Resena", back_populates="paciente")


class EstadoTurno(Base):
    __tablename__ = "estado_turno"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(50), nullable=False)

    turnos = relationship("Turno", back_populates="estado")


class Turno(Base):
    __tablename__ = "turno"

    id_turno = Column(Integer, primary_key=True, index=True)
    notas = Column(Text, nullable=True)
    fecha_hora = Column(DateTime, nullable=False)
    id_pacientes = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    id_medicos = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    id_estado = Column(Integer, ForeignKey("estado_turno.id"), nullable=False)

    paciente = relationship("Paciente", back_populates="turnos")
    medico = relationship("Medico", back_populates="turnos")
    estado = relationship("EstadoTurno", back_populates="turnos")


class Resena(Base):
    __tablename__ = "resenas"

    id_resena = Column(Integer, primary_key=True, index=True)
    estrellas = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    id_paciente = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    id_medico = Column(Integer, ForeignKey("medicos.id"), nullable=False)

    paciente = relationship("Paciente", back_populates="resenas")
    medico = relationship("Medico", back_populates="resenas")


class Recomienda(Base):
    __tablename__ = "recomienda"

    id_medico = Column(Integer, ForeignKey("medicos.id"), primary_key=True)
    id_medico_recomendado = Column(Integer, ForeignKey("medicos.id"), primary_key=True)

    medico = relationship("Medico", foreign_keys=[id_medico], back_populates="recomendaciones_dadas")
    medico_recomendado = relationship("Medico", foreign_keys=[id_medico_recomendado], back_populates="recomendaciones_recibidas")
