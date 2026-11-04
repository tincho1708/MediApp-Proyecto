from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session, joinedload, undefer
from typing import List, Optional
from urllib.parse import quote

from database import get_db
from models import Devolucion, Turno, EstadoTurno, Medico
from schemas import DevolucionResponse
from deps import get_current_user, solo_medico, solo_paciente

router = APIRouter(prefix="/devoluciones", tags=["Devoluciones"])

TIPOS_PERMITIDOS = {"application/pdf", "image/jpeg", "image/png"}
TAMANO_MAXIMO = 10 * 1024 * 1024


@router.post("", response_model=DevolucionResponse, status_code=201)
async def enviar_devolucion(
    id_turno: int = Form(...),
    contenido: Optional[str] = Form(None),
    archivo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    medico_id = int(user["sub"])

    turno = (
        db.query(Turno)
        .join(EstadoTurno)
        .filter(
            Turno.id_turno == id_turno,
            Turno.id_medicos == medico_id,
            EstadoTurno.estado == "aceptado",
        )
        .first()
    )
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado o no aceptado")

    if db.query(Devolucion).filter(Devolucion.id_turno == id_turno).first():
        raise HTTPException(status_code=409, detail="Este turno ya tiene una devolución")

    contenido = (contenido or "").strip() or None
    if not contenido and not archivo:
        raise HTTPException(status_code=400, detail="Escribí la devolución o subí un archivo")

    archivo_datos = None
    if archivo:
        if archivo.content_type not in TIPOS_PERMITIDOS:
            raise HTTPException(status_code=400, detail="El archivo tiene que ser PDF, JPG o PNG")
        archivo_datos = await archivo.read(TAMANO_MAXIMO + 1)
        if not archivo_datos:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        if len(archivo_datos) > TAMANO_MAXIMO:
            raise HTTPException(status_code=400, detail="El archivo no puede superar los 10 MB")

    devolucion = Devolucion(
        id_medico=medico_id,
        id_paciente=turno.id_pacientes,
        id_turno=id_turno,
        contenido=contenido,
        archivo_nombre=archivo.filename if archivo else None,
        archivo_tipo=archivo.content_type if archivo else None,
        archivo_datos=archivo_datos,
    )
    db.add(devolucion)
    db.commit()
    return (
        db.query(Devolucion)
        .options(joinedload(Devolucion.medico).joinedload(Medico.especialidades))
        .filter(Devolucion.id == devolucion.id)
        .first()
    )


@router.get("/turnos-con-devolucion", response_model=List[int])
def turnos_con_devolucion(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    filas = (
        db.query(Devolucion.id_turno)
        .filter(Devolucion.id_medico == int(user["sub"]), Devolucion.id_turno.isnot(None))
        .all()
    )
    return [fila.id_turno for fila in filas]


@router.get("/enviadas", response_model=List[DevolucionResponse])
def devoluciones_enviadas(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    return (
        db.query(Devolucion)
        .options(joinedload(Devolucion.medico).joinedload(Medico.especialidades))
        .filter(Devolucion.id_medico == int(user["sub"]))
        .order_by(Devolucion.fecha.desc())
        .all()
    )


@router.get("/mis-devoluciones", response_model=List[DevolucionResponse])
def mis_devoluciones(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_paciente),
):
    return (
        db.query(Devolucion)
        .options(joinedload(Devolucion.medico).joinedload(Medico.especialidades))
        .filter(Devolucion.id_paciente == int(user["sub"]))
        .order_by(Devolucion.fecha.desc())
        .all()
    )


@router.get("/{devolucion_id}/archivo")
def descargar_archivo(
    devolucion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    devolucion = (
        db.query(Devolucion)
        .options(undefer(Devolucion.archivo_datos))
        .filter(Devolucion.id == devolucion_id)
        .first()
    )
    if not devolucion or not devolucion.archivo_datos:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    dueno = devolucion.id_paciente if user.get("tipo") == "paciente" else devolucion.id_medico
    if dueno != int(user["sub"]):
        raise HTTPException(status_code=403, detail="No tenés permiso para acceder a este archivo")

    return Response(
        content=devolucion.archivo_datos,
        media_type=devolucion.archivo_tipo,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(devolucion.archivo_nombre)}"},
    )


@router.patch("/{devolucion_id}/leer", response_model=DevolucionResponse)
def marcar_leida(
    devolucion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_paciente),
):
    devolucion = (
        db.query(Devolucion)
        .options(joinedload(Devolucion.medico).joinedload(Medico.especialidades))
        .filter(Devolucion.id == devolucion_id)
        .first()
    )
    if not devolucion:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")
    if devolucion.id_paciente != int(user["sub"]):
        raise HTTPException(status_code=403, detail="No tenés permiso para acceder a esta devolución")

    devolucion.leida = True
    db.commit()
    db.refresh(devolucion)
    return devolucion
