from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from database import get_db
from models import Turno, EstadoTurno, Medico, Paciente, HorarioMedico
from schemas import TurnoCreate, TurnoResponse
from deps import get_current_user, solo_paciente, solo_medico

router = APIRouter(prefix="/turnos", tags=["Turnos"])


def _get_estado(db: Session, nombre: str) -> EstadoTurno:
    estado = db.query(EstadoTurno).filter(EstadoTurno.estado == nombre).first()
    if not estado:
        raise HTTPException(status_code=500, detail=f"Estado '{nombre}' no encontrado en la base de datos")
    return estado


@router.post("", response_model=TurnoResponse, status_code=201)
def solicitar_turno(
    data: TurnoCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_paciente),
):
    paciente_id = int(user["sub"])

    if not db.query(Medico).filter(Medico.id == data.medico_id, Medico.email_verificado == True).first():
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    if data.fecha_hora <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="La fecha debe ser futura")

    dia_semana = data.fecha_hora.weekday()
    hora = data.fecha_hora.hour
    disponible = db.query(HorarioMedico).filter(
        HorarioMedico.id_medico == data.medico_id,
        HorarioMedico.dia_semana == dia_semana,
        HorarioMedico.hora == hora,
    ).first()
    if not disponible:
        raise HTTPException(status_code=400, detail="El médico no está disponible en ese horario")

    solapado = db.query(Turno).join(EstadoTurno).filter(
        Turno.id_medicos == data.medico_id,
        Turno.fecha_hora == data.fecha_hora,
        EstadoTurno.estado.in_(["pendiente", "aceptado"]),
    ).first()
    if solapado:
        raise HTTPException(status_code=400, detail="El médico ya tiene un turno en ese horario")

    estado_pendiente = _get_estado(db, "pendiente")
    turno = Turno(
        id_pacientes=paciente_id,
        id_medicos=data.medico_id,
        fecha_hora=data.fecha_hora,
        notas=data.notas,
        id_estado=estado_pendiente.id,
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return db.query(Turno).options(joinedload(Turno.estado), joinedload(Turno.paciente), joinedload(Turno.medico).joinedload(Medico.especialidades)).filter(Turno.id_turno == turno.id_turno).first()


@router.get("/mis-turnos", response_model=List[TurnoResponse])
def mis_turnos(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Turno).options(joinedload(Turno.estado), joinedload(Turno.paciente), joinedload(Turno.medico).joinedload(Medico.especialidades))

    if user["tipo"] == "paciente":
        query = query.filter(Turno.id_pacientes == int(user["sub"]))
    else:
        query = query.filter(Turno.id_medicos == int(user["sub"]))

    return query.order_by(Turno.fecha_hora).all()


@router.patch("/{turno_id}/aceptar", response_model=TurnoResponse)
def aceptar_turno(
    turno_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    turno = db.query(Turno).options(joinedload(Turno.estado), joinedload(Turno.paciente), joinedload(Turno.medico).joinedload(Medico.especialidades)).filter(Turno.id_turno == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    if turno.id_medicos != int(user["sub"]):
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar este turno")
    if turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden aceptar turnos pendientes")

    turno.id_estado = _get_estado(db, "aceptado").id
    db.commit()
    db.refresh(turno)
    return turno


@router.patch("/{turno_id}/rechazar", response_model=TurnoResponse)
def rechazar_turno(
    turno_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    turno = db.query(Turno).options(joinedload(Turno.estado), joinedload(Turno.paciente), joinedload(Turno.medico).joinedload(Medico.especialidades)).filter(Turno.id_turno == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    if turno.id_medicos != int(user["sub"]):
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar este turno")
    if turno.estado.estado != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden rechazar turnos pendientes")

    turno.id_estado = _get_estado(db, "rechazado").id
    db.commit()
    db.refresh(turno)
    return turno


@router.patch("/{turno_id}/cancelar", response_model=TurnoResponse)
def cancelar_turno(
    turno_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    turno = db.query(Turno).options(joinedload(Turno.estado), joinedload(Turno.paciente), joinedload(Turno.medico).joinedload(Medico.especialidades)).filter(Turno.id_turno == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    es_paciente_del_turno = user["tipo"] == "paciente" and turno.id_pacientes == int(user["sub"])
    es_medico_del_turno = user["tipo"] == "medico" and turno.id_medicos == int(user["sub"])
    if not es_paciente_del_turno and not es_medico_del_turno:
        raise HTTPException(status_code=403, detail="No tenés permiso para cancelar este turno")

    if turno.estado.estado == "cancelado":
        raise HTTPException(status_code=400, detail="El turno ya está cancelado")

    turno.id_estado = _get_estado(db, "cancelado").id
    db.commit()
    db.refresh(turno)
    return turno
