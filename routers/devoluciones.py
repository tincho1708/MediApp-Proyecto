from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Devolucion, Turno, EstadoTurno, Medico, Paciente
from schemas import DevolucionCreate, DevolucionResponse
from deps import solo_medico, solo_paciente

router = APIRouter(prefix="/devoluciones", tags=["Devoluciones"])


@router.post("", response_model=DevolucionResponse, status_code=201)
def enviar_devolucion(
    data: DevolucionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    medico_id = int(user["sub"])

    paciente = db.query(Paciente).filter(Paciente.id == data.id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Solo puede enviar devolución a pacientes con los que tuvo un turno aceptado
    turno_en_comun = (
        db.query(Turno)
        .join(EstadoTurno)
        .filter(
            Turno.id_medicos == medico_id,
            Turno.id_pacientes == data.id_paciente,
            EstadoTurno.estado == "aceptado",
        )
        .first()
    )
    if not turno_en_comun:
        raise HTTPException(
            status_code=403,
            detail="Solo podés enviar devoluciones a pacientes con los que tuviste un turno aceptado",
        )

    if data.id_turno:
        turno_ref = db.query(Turno).filter(
            Turno.id_turno == data.id_turno,
            Turno.id_medicos == medico_id,
            Turno.id_pacientes == data.id_paciente,
        ).first()
        if not turno_ref:
            raise HTTPException(status_code=404, detail="Turno de referencia no encontrado o no pertenece a esta relación")

    devolucion = Devolucion(
        id_medico=medico_id,
        id_paciente=data.id_paciente,
        id_turno=data.id_turno,
        contenido=data.contenido,
    )
    db.add(devolucion)
    db.commit()
    db.refresh(devolucion)
    return (
        db.query(Devolucion)
        .options(joinedload(Devolucion.medico).joinedload(Medico.especialidades))
        .filter(Devolucion.id == devolucion.id)
        .first()
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
