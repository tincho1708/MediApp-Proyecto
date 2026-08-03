from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from database import get_db
from models import Medico, Especialidad
from schemas import MedicoPublicoResponse, EspecialidadResponse

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
    query = db.query(Medico).options(joinedload(Medico.especialidad)).filter(
        Medico.email_verificado == True
    )

    if nombre:
        busqueda = f"%{nombre}%"
        query = query.filter(
            Medico.nombre.ilike(busqueda) | Medico.apellido.ilike(busqueda)
        )

    if especialidad_id:
        query = query.filter(Medico.especialidad_id == especialidad_id)

    return query.order_by(Medico.apellido, Medico.nombre).all()


@router.get("/medicos/{medico_id}", response_model=MedicoPublicoResponse)
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = (
        db.query(Medico)
        .options(joinedload(Medico.especialidad))
        .filter(Medico.id == medico_id, Medico.email_verificado == True)
        .first()
    )
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return medico
