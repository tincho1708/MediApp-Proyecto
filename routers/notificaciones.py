from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Notificacion, Turno, EstadoTurno
from schemas import NotificacionResponse
from deps import solo_medico

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def _get_estado(db: Session, nombre: str) -> EstadoTurno:
    estado = db.query(EstadoTurno).filter(EstadoTurno.estado == nombre).first()
    if not estado:
        raise HTTPException(status_code=500, detail=f"Estado '{nombre}' no encontrado")
    return estado


def _get_notificacion(db: Session, notificacion_id: int, medico_id: int) -> Notificacion:
    notificacion = (
        db.query(Notificacion)
        .options(joinedload(Notificacion.turno).joinedload(Turno.estado))
        .filter(Notificacion.id == notificacion_id)
        .first()
    )
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if notificacion.id_medico != medico_id:
        raise HTTPException(status_code=403, detail="No tenés permiso para acceder a esta notificación")
    return notificacion


@router.get("", response_model=List[NotificacionResponse])
def listar_notificaciones(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    return (
        db.query(Notificacion)
        .options(joinedload(Notificacion.turno).joinedload(Turno.estado))
        .filter(Notificacion.id_medico == int(user["sub"]), Notificacion.leida == False)
        .order_by(Notificacion.fecha.desc())
        .all()
    )


@router.patch("/{notificacion_id}/aceptar", response_model=NotificacionResponse)
def aceptar_turno(
    notificacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    notificacion = _get_notificacion(db, notificacion_id, int(user["sub"]))

    if notificacion.leida:
        raise HTTPException(status_code=400, detail="Esta notificación ya fue respondida")
    if notificacion.turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="El turno ya no está pendiente")

    notificacion.turno.id_estado = _get_estado(db, "aceptado").id
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


@router.patch("/{notificacion_id}/rechazar", response_model=NotificacionResponse)
def rechazar_turno(
    notificacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    notificacion = _get_notificacion(db, notificacion_id, int(user["sub"]))

    if notificacion.leida:
        raise HTTPException(status_code=400, detail="Esta notificación ya fue respondida")
    if notificacion.turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="El turno ya no está pendiente")

    notificacion.turno.id_estado = _get_estado(db, "rechazado").id
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion
