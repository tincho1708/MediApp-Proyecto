import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session, undefer

from database import get_db
from models import Medico, Paciente
from deps import get_current_user

router = APIRouter(prefix="/fotos", tags=["Fotos"])

TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANO_MAXIMO = 5 * 1024 * 1024


@router.put("/mia")
async def cambiar_mi_foto(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    modelo = Medico if user["tipo"] == "medico" else Paciente
    usuario = db.query(modelo).filter(modelo.id == int(user["sub"])).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="La foto tiene que ser JPG, PNG o WEBP")
    datos = await archivo.read(TAMANO_MAXIMO + 1)
    if not datos:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(datos) > TAMANO_MAXIMO:
        raise HTTPException(status_code=400, detail="La foto no puede superar los 5 MB")

    usuario.foto_clave = uuid.uuid4().hex
    usuario.foto_tipo = archivo.content_type
    usuario.foto_datos = datos
    db.commit()
    return {"foto": usuario.foto}


@router.get("/{clave}")
def ver_foto(clave: str, db: Session = Depends(get_db)):
    for modelo in (Medico, Paciente):
        usuario = db.query(modelo).options(undefer(modelo.foto_datos)).filter(modelo.foto_clave == clave).first()
        if usuario:
            return Response(
                content=usuario.foto_datos,
                media_type=usuario.foto_tipo,
                headers={"Cache-Control": "public, max-age=31536000, immutable"},
            )
    raise HTTPException(status_code=404, detail="Foto no encontrada")
