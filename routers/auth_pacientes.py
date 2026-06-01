from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from database import get_db
from models import Paciente
from schemas import PacienteRegister, PacienteLogin, PacienteResponse, Token, Message
from auth_utils import hash_password, verify_password, create_access_token
from email_utils import send_verification_email

router = APIRouter(prefix="/auth/pacientes", tags=["Auth Pacientes"])


@router.post("/registro", response_model=Message, status_code=status.HTTP_201_CREATED)
def registrar_paciente(data: PacienteRegister, db: Session = Depends(get_db)):
    if db.query(Paciente).filter(Paciente.mail == data.mail).first():
        raise HTTPException(status_code=400, detail="El mail ya está registrado")
    if db.query(Paciente).filter(Paciente.dni == data.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")

    token = str(uuid.uuid4())
    paciente = Paciente(
        nombre=data.nombre,
        apellido=data.apellido,
        dni=data.dni,
        telefono=data.telefono,
        mail=data.mail,
        password_hash=hash_password(data.password),
        email_verificado=False,
        verification_token=token,
        verification_token_expires=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(paciente)
    db.commit()

    send_verification_email(data.mail, data.nombre, token, "pacientes")
    return {"message": "Registro exitoso. Revisá tu mail para verificar tu cuenta."}


@router.get("/verificar", response_model=Message)
def verificar_email_paciente(token: str, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.verification_token == token).first()
    if not paciente:
        raise HTTPException(status_code=400, detail="Token inválido")
    if paciente.verification_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El token expiró. Registrate de nuevo.")
    if paciente.email_verificado:
        return {"message": "El mail ya fue verificado anteriormente."}

    paciente.email_verificado = True
    paciente.verification_token = None
    paciente.verification_token_expires = None
    db.commit()
    return {"message": "Mail verificado correctamente. Ya podés iniciar sesión."}


@router.post("/login", response_model=Token)
def login_paciente(data: PacienteLogin, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.mail == data.mail).first()
    if not paciente or not verify_password(data.password, paciente.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not paciente.email_verificado:
        raise HTTPException(status_code=403, detail="Debés verificar tu mail antes de iniciar sesión")

    token = create_access_token({"sub": str(paciente.id), "tipo": "paciente"})
    return {"access_token": token, "token_type": "bearer"}
