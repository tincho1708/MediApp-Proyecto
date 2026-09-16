from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date, datetime, timedelta

from database import get_db
from models import Medico, Especialidad, HorarioMedico, Turno, EstadoTurno
from schemas import MedicoPublicoResponse, EspecialidadResponse, HorarioResponse, HorarioUpdate
from deps import solo_medico

router = APIRouter(tags=["Médicos"])


@router.get("/especialidades", response_model=List[EspecialidadResponse])
def listar_especialidades(db: Session = Depends(get_db)):
    return db.query(Especialidad).order_by(Especialidad.nombre_especialidad).all()


@router.get("/medicos", response_model=List[MedicoPublicoResponse])
def buscar_medicos(
    nombre: Optional[str] = None,
    especialidad_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Medico).options(joinedload(Medico.especialidades)).filter(
        Medico.email_verificado == True
    )

    if nombre:
        busqueda = f"%{nombre}%"
        query = query.filter(
            Medico.nombre.ilike(busqueda) | Medico.apellido.ilike(busqueda)
        )

    if especialidad_id:
        query = query.filter(Medico.especialidades.any(Especialidad.id_especialidad == especialidad_id))

    return query.order_by(Medico.apellido, Medico.nombre).all()


@router.get("/medicos/{medico_id}/horarios", response_model=List[HorarioResponse])
def obtener_horarios(medico_id: int, db: Session = Depends(get_db)):
    return db.query(HorarioMedico).filter(
        HorarioMedico.id_medico == medico_id
    ).order_by(HorarioMedico.dia_semana, HorarioMedico.hora).all()


@router.get("/medicos/{medico_id}/horarios-ocupados", response_model=List[int])
def obtener_horarios_ocupados(medico_id: int, fecha: date, db: Session = Depends(get_db)):
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = inicio + timedelta(days=1)

    turnos = db.query(Turno).join(EstadoTurno).filter(
        Turno.id_medicos == medico_id,
        Turno.fecha_hora >= inicio,
        Turno.fecha_hora < fin,
        EstadoTurno.estado.in_(["pendiente", "aceptado"]),
    ).all()

    return [t.fecha_hora.hour for t in turnos]


@router.put("/medicos/mis-horarios", response_model=List[HorarioResponse])
def actualizar_horarios(
    data: HorarioUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    medico_id = int(user["sub"])
    db.query(HorarioMedico).filter(HorarioMedico.id_medico == medico_id).delete()
    for h in data.horarios:
        dia = h.get("dia_semana")
        hora = h.get("hora")
        if dia is None or hora is None or not (0 <= dia <= 6) or not (0 <= hora <= 23):
            raise HTTPException(status_code=400, detail="Horario inválido")
        db.add(HorarioMedico(id_medico=medico_id, dia_semana=dia, hora=hora))
    db.commit()
    return db.query(HorarioMedico).filter(
        HorarioMedico.id_medico == medico_id
    ).order_by(HorarioMedico.dia_semana, HorarioMedico.hora).all()


@router.get("/medicos/{medico_id}", response_model=MedicoPublicoResponse)
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = (
        db.query(Medico)
        .options(joinedload(Medico.especialidades))
        .filter(Medico.id == medico_id, Medico.email_verificado == True)
        .first()
    )
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return medico
