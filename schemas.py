from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


# --- Medico ---

class MedicoRegister(BaseModel):
    nombre: str
    apellido: str
    dni: str
    telefono: Optional[str] = None
    mail: EmailStr
    password: str
    especialidad_id: int


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
    apellido: str
    dni: str
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


# --- Auth responses ---

class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str
