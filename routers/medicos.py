from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date

from database import get_db
from models import Medico, Especialidad, HorarioMedico, FechaBloqueada
from schemas import MedicoPublicoResponse, EspecialidadResponse, HorarioResponse, HorarioUpdate, ConfiguracionTurnos
from deps import solo_medico
from agenda import turnos_libres

DURACIONES = {15, 20, 30, 45, 60}
MARGENES = {0, 5, 10, 15}

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


@router.get("/medicos/{medico_id}/turnos-libres", response_model=List[str])
def obtener_turnos_libres(medico_id: int, fecha: date, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter(Medico.id == medico_id, Medico.email_verificado == True).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return [t.strftime("%H:%M") for t in turnos_libres(db, medico, fecha)]


@router.get("/medicos/mi-configuracion", response_model=ConfiguracionTurnos)
def mi_configuracion(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    medico = db.query(Medico).filter(Medico.id == int(user["sub"])).first()
    fechas = db.query(FechaBloqueada).filter(FechaBloqueada.id_medico == medico.id).order_by(FechaBloqueada.fecha).all()
    return {
        "duracion_turno": medico.duracion_turno,
        "margen_turno": medico.margen_turno,
        "fechas_bloqueadas": [f.fecha for f in fechas],
    }


@router.put("/medicos/mi-configuracion", response_model=ConfiguracionTurnos)
def actualizar_configuracion(
    data: ConfiguracionTurnos,
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    if data.duracion_turno not in DURACIONES:
        raise HTTPException(status_code=400, detail="Duración de turno inválida")
    if data.margen_turno not in MARGENES:
        raise HTTPException(status_code=400, detail="Tiempo entre turnos inválido")

    medico = db.query(Medico).filter(Medico.id == int(user["sub"])).first()
    medico.duracion_turno = data.duracion_turno
    medico.margen_turno = data.margen_turno

    db.query(FechaBloqueada).filter(FechaBloqueada.id_medico == medico.id).delete()
    for fecha in sorted(set(data.fechas_bloqueadas)):
        db.add(FechaBloqueada(id_medico=medico.id, fecha=fecha))
    db.commit()
    return mi_configuracion(db, user)


@router.get("/medicos/mis-horarios", response_model=List[HorarioResponse])
def mis_horarios(
    db: Session = Depends(get_db),
    user: dict = Depends(solo_medico),
):
    medico_id = int(user["sub"])
    return db.query(HorarioMedico).filter(
        HorarioMedico.id_medico == medico_id
    ).order_by(HorarioMedico.dia_semana, HorarioMedico.hora).all()


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
