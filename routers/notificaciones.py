from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Notificacion, NotificacionPaciente, Turno, EstadoTurno, Medico
from schemas import NotificacionResponse, NotificacionPacienteResponse, ConteoNoLeidasResponse
from deps import solo_medico, solo_paciente, get_current_user

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def _get_estado(db: Session, nombre: str) -> EstadoTurno:
    estado = db.query(EstadoTurno).filter(EstadoTurno.estado == nombre).first()
    if not estado:
        raise HTTPException(status_code=500, detail=f"Estado '{nombre}' no encontrado")
    return estado


def _get_notificacion_medico(db: Session, notificacion_id: int, medico_id: int) -> Notificacion:
    notificacion = (
        db.query(Notificacion)
        .options(
            joinedload(Notificacion.turno)
            .joinedload(Turno.estado),
            joinedload(Notificacion.turno)
            .joinedload(Turno.paciente),
            joinedload(Notificacion.turno)
            .joinedload(Turno.medico)
            .joinedload(Medico.especialidades),
        )
        .filter(Notificacion.id == notificacion_id)
        .first()
    )
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if notificacion.id_medico != medico_id:
        raise HTTPException(status_code=403, detail="No tenés permiso para acceder a esta notificación")
    return notificacion


# ── Médico ──────────────────────────────────────────────────────────────────

@router.get("", response_model=List[NotificacionResponse])
def listar_notificaciones_medico(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    return (
        db.query(Notificacion)
        .options(
            joinedload(Notificacion.turno).joinedload(Turno.estado),
            joinedload(Notificacion.turno).joinedload(Turno.paciente),
            joinedload(Notificacion.turno).joinedload(Turno.medico).joinedload(Medico.especialidades),
        )
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
    notificacion = _get_notificacion_medico(db, notificacion_id, int(user["sub"]))

    if notificacion.leida:
        raise HTTPException(status_code=400, detail="Esta notificación ya fue respondida")
    if notificacion.turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="El turno ya no está pendiente")

    notificacion.turno.id_estado = _get_estado(db, "aceptado").id
    notificacion.leida = True

    turno = notificacion.turno
    fecha_str = turno.fecha_hora.strftime("%d/%m/%Y a las %H:%M")
    notif_paciente = NotificacionPaciente(
        id_paciente=turno.id_pacientes,
        id_turno=turno.id_turno,
        mensaje=f"Tu turno del {fecha_str} fue aceptado.",
    )
    db.add(notif_paciente)
    db.commit()
    db.refresh(notificacion)
    return notificacion


@router.patch("/{notificacion_id}/rechazar", response_model=NotificacionResponse)
def rechazar_turno(
    notificacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    notificacion = _get_notificacion_medico(db, notificacion_id, int(user["sub"]))

    if notificacion.leida:
        raise HTTPException(status_code=400, detail="Esta notificación ya fue respondida")
    if notificacion.turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="El turno ya no está pendiente")

    notificacion.turno.id_estado = _get_estado(db, "rechazado").id
    notificacion.leida = True

    turno = notificacion.turno
    fecha_str = turno.fecha_hora.strftime("%d/%m/%Y a las %H:%M")
    notif_paciente = NotificacionPaciente(
        id_paciente=turno.id_pacientes,
        id_turno=turno.id_turno,
        mensaje=f"Tu turno del {fecha_str} fue rechazado.",
    )
    db.add(notif_paciente)
    db.commit()
    db.refresh(notificacion)
    return notificacion


# ── Paciente ─────────────────────────────────────────────────────────────────

@router.get("/paciente", response_model=List[NotificacionPacienteResponse])
def listar_notificaciones_paciente(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_paciente),
):
    return (
        db.query(NotificacionPaciente)
        .options(
            joinedload(NotificacionPaciente.turno).joinedload(Turno.estado),
            joinedload(NotificacionPaciente.turno).joinedload(Turno.paciente),
            joinedload(NotificacionPaciente.turno).joinedload(Turno.medico).joinedload(Medico.especialidades),
        )
        .filter(NotificacionPaciente.id_paciente == int(user["sub"]), NotificacionPaciente.leida == False)
        .order_by(NotificacionPaciente.fecha.desc())
        .all()
    )


@router.patch("/paciente/{notificacion_id}/leer", response_model=NotificacionPacienteResponse)
def leer_notificacion_paciente(
    notificacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_paciente),
):
    notificacion = (
        db.query(NotificacionPaciente)
        .options(
            joinedload(NotificacionPaciente.turno).joinedload(Turno.estado),
            joinedload(NotificacionPaciente.turno).joinedload(Turno.paciente),
            joinedload(NotificacionPaciente.turno).joinedload(Turno.medico).joinedload(Medico.especialidades),
        )
        .filter(NotificacionPaciente.id == notificacion_id)
        .first()
    )
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if notificacion.id_paciente != int(user["sub"]):
        raise HTTPException(status_code=403, detail="No tenés permiso para acceder a esta notificación")

    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


# ── Conteo (ambos tipos) ──────────────────────────────────────────────────────

@router.get("/no-leidas", response_model=ConteoNoLeidasResponse)
def contar_no_leidas(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user["tipo"] == "medico":
        count = db.query(Notificacion).filter(
            Notificacion.id_medico == int(user["sub"]),
            Notificacion.leida == False,
        ).count()
    else:
        count = db.query(NotificacionPaciente).filter(
            NotificacionPaciente.id_paciente == int(user["sub"]),
            NotificacionPaciente.leida == False,
        ).count()
    return {"count": count}
