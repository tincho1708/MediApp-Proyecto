from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from database import get_db
from models import Medico, Especialidad, HorarioMedico
from schemas import MedicoRegister, MedicoLogin, Token, Message, RegistroMedicoResponse, EspecialidadesSetup
from auth_utils import hash_password, verify_password, create_access_token
from email_utils import send_verification_email

router = APIRouter(prefix="/auth/medicos", tags=["Auth Medicos"])


@router.post("/registro", response_model=RegistroMedicoResponse, status_code=status.HTTP_201_CREATED)
def registrar_medico(data: MedicoRegister, db: Session = Depends(get_db)):
    if db.query(Medico).filter(Medico.mail == data.mail).first():
        raise HTTPException(status_code=400, detail="El mail ya está registrado")

    verification_token = str(uuid.uuid4())
    setup_token = str(uuid.uuid4())

    medico = Medico(
        nombre=data.nombre,
        apellido="",
        telefono=data.telefono,
        mail=data.mail,
        password_hash=hash_password(data.password),
        email_verificado=False,
        verification_token=verification_token,
        verification_token_expires=datetime.utcnow() + timedelta(hours=24),
        setup_token=setup_token,
    )
    db.add(medico)
    db.flush()

    for dia in range(5):
        for hora in range(9, 17):
            db.add(HorarioMedico(id_medico=medico.id, dia_semana=dia, hora=hora))

    try:
        send_verification_email(data.mail, data.nombre, verification_token, "medicos")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al enviar el mail de verificación: {str(e)}")

    db.commit()
    return {"message": "Registro exitoso. Revisá tu mail para verificar tu cuenta.", "medico_id": medico.id, "setup_token": setup_token}


@router.post("/setup-especialidades", response_model=Message, status_code=200)
def setup_especialidades(data: EspecialidadesSetup, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.setup_token == data.setup_token).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Token de setup inválido")

    if len(data.especialidad_ids) > 3:
        raise HTTPException(status_code=400, detail="Un médico puede tener como máximo 3 especialidades")

    especialidades = db.query(Especialidad).filter(
        Especialidad.id_especialidad.in_(data.especialidad_ids)
    ).all()
    if len(especialidades) != len(set(data.especialidad_ids)):
        raise HTTPException(status_code=400, detail="Una o más especialidades no existen")

    medico.especialidades = especialidades
    medico.setup_token = None
    db.commit()
    return {"message": "Especialidades asignadas correctamente"}


def _html(titulo: str, mensaje: str, color: str = "#2563eb") -> HTMLResponse:
    return HTMLResponse(content=f"""
    <html><head><meta charset="utf-8"><title>{titulo}</title></head>
    <body style="font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f3f4f6;">
      <div style="text-align:center;padding:40px;background:white;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.1);max-width:400px;">
        <h2 style="color:{color};">{titulo}</h2>
        <p style="color:#374151;">{mensaje}</p>
      </div>
    </body></html>
    """)


@router.get("/verificar")
def verificar_email_medico(token: str, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.verification_token == token).first()
    if not medico:
        return _html("Token inválido", "El enlace no es válido.", "#dc2626")
    if medico.verification_token_expires < datetime.utcnow():
        return _html("Enlace expirado", "El enlace expiró. Registrate de nuevo.", "#dc2626")
    if medico.email_verificado:
        return _html("Ya verificado", "Tu cuenta ya fue verificada anteriormente.")

    medico.email_verificado = True
    medico.verification_token = None
    medico.verification_token_expires = None
    db.commit()
    return _html("¡Cuenta verificada!", "Tu cuenta fue verificada correctamente. Ya podés iniciar sesión.")


@router.post("/login", response_model=Token)
def login_medico(data: MedicoLogin, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.mail == data.mail).first()
    if not medico or not verify_password(data.password, medico.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not medico.email_verificado:
        raise HTTPException(status_code=403, detail="Debés verificar tu mail antes de iniciar sesión")

    token = create_access_token({"sub": str(medico.id), "tipo": "medico"})
    return {"access_token": token, "token_type": "bearer", "nombre": medico.nombre}
