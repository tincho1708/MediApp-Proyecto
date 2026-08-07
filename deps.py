from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_utils import decode_access_token

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


def solo_paciente(user: dict = Depends(get_current_user)) -> dict:
    if user.get("tipo") != "paciente":
        raise HTTPException(status_code=403, detail="Solo los pacientes pueden realizar esta acción")
    return user


def solo_medico(user: dict = Depends(get_current_user)) -> dict:
    if user.get("tipo") != "medico":
        raise HTTPException(status_code=403, detail="Solo los médicos pueden realizar esta acción")
    return user
