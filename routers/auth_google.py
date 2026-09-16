from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
import random
import os
import uuid
from jose import jwt
from dotenv import load_dotenv

from database import get_db
from models import Medico, Paciente, HorarioMedico
from auth_utils import create_access_token
from email_utils import send_pin_email

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")

router = APIRouter(prefix="/auth/google", tags=["Auth Google"])


def verify_auth0_token(token: str) -> dict:
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = httpx.get(jwks_url).json()
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {"kty": key["kty"], "kid": key["kid"],
                           "use": key["use"], "n": key["n"], "e": key["e"]}
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Clave de firma no encontrada")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTH0_CLIENT_ID,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token de Google inválido")


def generar_pin() -> str:
    return str(random.randint(100000, 999999))


# --- Schemas ---

class GoogleRegistroRequest(BaseModel):
    id_token: str
    tipo: str  # "medico" o "paciente"


class PinVerificacionRequest(BaseModel):
    email: str
    pin: str
    tipo: str  # "medico" o "paciente"


class GoogleLoginRequest(BaseModel):
    id_token: str
    tipo: str


# --- Endpoints ---

@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro_google(data: GoogleRegistroRequest, db: Session = Depends(get_db)):
    if data.tipo not in ("medico", "paciente"):
        raise HTTPException(status_code=400, detail="Tipo debe ser 'medico' o 'paciente'")

    payload = verify_auth0_token(data.id_token)
    email = payload.get("email")
    nombre = payload.get("given_name") or payload.get("name", "").split()[0]
    apellido = payload.get("family_name") or (payload.get("name", "").split()[-1] if " " in payload.get("name", "") else "")
    google_id = payload.get("sub")

    if not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el email de Google")

    pin = generar_pin()
    if data.tipo == "medico":
        if db.query(Medico).filter(Medico.mail == email).first():
            raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese mail")
        setup_token = str(uuid.uuid4())
        usuario = Medico(
            nombre=nombre, apellido=apellido, mail=email,
            google_id=google_id, email_verificado=False,
            setup_token=setup_token,
            pin_verificacion=pin,
            pin_expires=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(usuario)
        db.flush()
        for dia in range(5):
            for hora in range(9, 17):
                db.add(HorarioMedico(id_medico=usuario.id, dia_semana=dia, hora=hora))
    else:
        if db.query(Paciente).filter(Paciente.mail == email).first():
            raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese mail")
        usuario = Paciente(
            nombre=nombre, apellido=apellido, mail=email,
            google_id=google_id, email_verificado=False,
            pin_verificacion=pin,
            pin_expires=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(usuario)

    db.commit()
    send_pin_email(email, nombre, pin)
    return {"message": "Cuenta creada. Te enviamos un PIN de 6 dígitos al mail para confirmar."}


@router.post("/verificar-pin")
def verificar_pin(data: PinVerificacionRequest, db: Session = Depends(get_db)):
    if data.tipo == "medico":
        usuario = db.query(Medico).filter(Medico.mail == data.email).first()
    else:
        usuario = db.query(Paciente).filter(Paciente.mail == data.email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.email_verificado:
        raise HTTPException(status_code=400, detail="El mail ya fue verificado")
    if not usuario.pin_verificacion or usuario.pin_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El PIN expiró. Volvé a registrarte.")
    if usuario.pin_verificacion != data.pin:
        raise HTTPException(status_code=400, detail="PIN incorrecto")

    usuario.email_verificado = True
    usuario.pin_verificacion = None
    usuario.pin_expires = None
    db.commit()

    token = create_access_token({"sub": str(usuario.id), "tipo": data.tipo})
    response = {"access_token": token, "token_type": "bearer", "nombre": usuario.nombre}

    if data.tipo == "medico" and usuario.setup_token:
        response["setup_token"] = usuario.setup_token
        response["medico_id"] = usuario.id

    return response


@router.post("/login")
def login_google(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    if data.tipo not in ("medico", "paciente"):
        raise HTTPException(status_code=400, detail="Tipo debe ser 'medico' o 'paciente'")

    payload = verify_auth0_token(data.id_token)
    google_id = payload.get("sub")

    if data.tipo == "medico":
        usuario = db.query(Medico).filter(Medico.google_id == google_id).first()
    else:
        usuario = db.query(Paciente).filter(Paciente.google_id == google_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="No existe cuenta con ese Google. Registrate primero.")
    if not usuario.email_verificado:
        raise HTTPException(status_code=403, detail="Cuenta pendiente de verificación de PIN")

    token = create_access_token({"sub": str(usuario.id), "tipo": data.tipo})
    return {"access_token": token, "token_type": "bearer", "nombre": usuario.nombre}
