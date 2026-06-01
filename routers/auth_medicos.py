from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from database import get_db
from models import Medico
from schemas import MedicoRegister, MedicoLogin, MedicoResponse, Token, Message
from auth_utils import hash_password, verify_password, create_access_token
from email_utils import send_verification_email

router = APIRouter(prefix="/auth/medicos", tags=["Auth Medicos"])


@router.post("/registro", response_model=Message, status_code=status.HTTP_201_CREATED)
def registrar_medico(data: MedicoRegister, db: Session = Depends(get_db)):
    if db.query(Medico).filter(Medico.mail == data.mail).first():
        raise HTTPException(status_code=400, detail="El mail ya está registrado")
    if db.query(Medico).filter(Medico.dni == data.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")

    token = str(uuid.uuid4())
    medico = Medico(
        nombre=data.nombre,
        apellido=data.apellido,
        dni=data.dni,
        telefono=data.telefono,
        mail=data.mail,
        especialidad_id=data.especialidad_id,
        password_hash=hash_password(data.password),
        email_verificado=False,
        verification_token=token,
        verification_token_expires=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(medico)
    db.commit()

    send_verification_email(data.mail, data.nombre, token, "medicos")
    return {"message": "Registro exitoso. Revisá tu mail para verificar tu cuenta."}


@router.get("/verificar", response_model=Message)
def verificar_email_medico(token: str, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.verification_token == token).first()
    if not medico:
        raise HTTPException(status_code=400, detail="Token inválido")
    if medico.verification_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El token expiró. Registrate de nuevo.")
    if medico.email_verificado:
        return {"message": "El mail ya fue verificado anteriormente."}

    medico.email_verificado = True
    medico.verification_token = None
    medico.verification_token_expires = None
    db.commit()
    return {"message": "Mail verificado correctamente. Ya podés iniciar sesión."}


@router.post("/login", response_model=Token)
def login_medico(data: MedicoLogin, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.mail == data.mail).first()
    if not medico or not verify_password(data.password, medico.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not medico.email_verificado:
        raise HTTPException(status_code=403, detail="Debés verificar tu mail antes de iniciar sesión")

    token = create_access_token({"sub": str(medico.id), "tipo": "medico"})
    return {"access_token": token, "token_type": "bearer"}
