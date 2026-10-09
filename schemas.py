from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import datetime


class EspecialidadResponse(BaseModel):
    id_especialidad: int
    nombre_especialidad: str

    class Config:
        from_attributes = True


class MedicoRegister(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    mail: EmailStr
    password: str


class MedicoLogin(BaseModel):
    mail: EmailStr
    password: str


class RegistroMedicoResponse(BaseModel):
    message: str
    medico_id: int
    setup_token: str


class EspecialidadesSetup(BaseModel):
    setup_token: str
    especialidad_ids: List[int] = Field(min_length=1, max_length=3)


class MedicoResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: Optional[str]
    telefono: Optional[str]
    mail: str
    especialidades: List[EspecialidadResponse]
    email_verificado: bool

    class Config:
        from_attributes = True


class MedicoPublicoResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    mail: str
    especialidades: List[EspecialidadResponse]

    class Config:
        from_attributes = True


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
    dni: Optional[str]
    telefono: Optional[str]
    mail: str
    email_verificado: bool

    class Config:
        from_attributes = True


class HorarioResponse(BaseModel):
    id: int
    dia_semana: int
    hora: int

    class Config:
        from_attributes = True


class HorarioUpdate(BaseModel):
    horarios: list[dict]


class TurnoCreate(BaseModel):
    medico_id: int
    fecha_hora: datetime.datetime
    notas: Optional[str] = None


class EstadoTurnoResponse(BaseModel):
    id: int
    estado: str

    class Config:
        from_attributes = True


class PacienteBasico(BaseModel):
    id: int
    nombre: str
    apellido: str

    class Config:
        from_attributes = True


class MedicoBasico(BaseModel):
    id: int
    nombre: str
    apellido: str
    especialidades: List[EspecialidadResponse]

    class Config:
        from_attributes = True


class TurnoResponse(BaseModel):
    id_turno: int
    fecha_hora: datetime.datetime
    creado_en: Optional[datetime.datetime]
    notas: Optional[str]
    id_pacientes: int
    id_medicos: int
    estado: EstadoTurnoResponse
    paciente: PacienteBasico
    medico: MedicoBasico

    class Config:
        from_attributes = True


class NotificacionResponse(BaseModel):
    id: int
    id_turno: int
    mensaje: str
    leida: bool
    fecha: datetime.datetime
    turno: TurnoResponse

    class Config:
        from_attributes = True


class DevolucionCreate(BaseModel):
    id_paciente: int
    contenido: str
    id_turno: Optional[int] = None


class DevolucionResponse(BaseModel):
    id: int
    contenido: str
    fecha: datetime.datetime
    leida: bool
    id_medico: int
    id_paciente: int
    id_turno: Optional[int]
    medico: "MedicoBasico"

    class Config:
        from_attributes = True


class MensajeChat(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class MediBotRequest(BaseModel):
    messages: List[MensajeChat] = Field(min_length=1, max_length=40)
    conversacion_id: Optional[int] = None


class MediBotResponse(BaseModel):
    respuesta: str
    conversacion_id: int
    herramientas_usadas: List[str] = []


class ConversacionResponse(BaseModel):
    id: int
    titulo: str
    creado_en: datetime.datetime

    class Config:
        from_attributes = True


class MensajeMediBotResponse(BaseModel):
    id: int
    rol: str
    contenido: str
    creado_en: datetime.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    nombre: str


class Message(BaseModel):
    message: str
