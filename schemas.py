from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


# --- Medico ---

class MedicoRegister(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    mail: EmailStr
    password: str
    especialidad_id: Optional[int] = None


class MedicoLogin(BaseModel):
    mail: EmailStr
    password: str


class MedicoResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    telefono: Optional[str]
    mail: str
    especialidad_id: Optional[int]
    email_verificado: bool

    class Config:
        from_attributes = True


# --- Paciente ---

class PacienteRegister(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    mail: EmailStr
    password: str


class PacienteLogin(BaseModel):
    mail: EmailStr
    password: str


class PacienteResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    telefono: Optional[str]
    mail: str
    email_verificado: bool

    class Config:
        from_attributes = True


# --- Especialidad ---

class EspecialidadResponse(BaseModel):
    id_especialidad: int
    nombre_especialidad: str

    class Config:
        from_attributes = True


# --- Medico público (buscador) ---

class MedicoPublicoResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    mail: str
    especialidad_id: Optional[int]
    especialidad: Optional[EspecialidadResponse]

    class Config:
        from_attributes = True


# --- Turnos ---

class TurnoCreate(BaseModel):
    medico_id: int
    fecha_hora: datetime.datetime
    notas: Optional[str] = None


class EstadoTurnoResponse(BaseModel):
    id: int
    estado: str

    class Config:
        from_attributes = True


class TurnoResponse(BaseModel):
    id_turno: int
    fecha_hora: datetime.datetime
    notas: Optional[str]
    id_pacientes: int
    id_medicos: int
    estado: EstadoTurnoResponse

    class Config:
        from_attributes = True


# --- Auth responses ---

class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str
