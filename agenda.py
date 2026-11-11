from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from models import EstadoTurno, FechaBloqueada, HorarioMedico, Medico, Turno


def _bloques(horas: list[int]) -> list[tuple[int, int]]:
    bloques = []
    for hora in sorted(horas):
        if bloques and bloques[-1][1] == hora:
            bloques[-1] = (bloques[-1][0], hora + 1)
        else:
            bloques.append((hora, hora + 1))
    return bloques


def turnos_libres(db: Session, medico: Medico, fecha: date, ahora: datetime | None = None) -> list[datetime]:
    bloqueada = db.query(FechaBloqueada).filter(FechaBloqueada.id_medico == medico.id, FechaBloqueada.fecha == fecha).first()
    if bloqueada:
        return []

    horas = [
        h.hora
        for h in db.query(HorarioMedico).filter(HorarioMedico.id_medico == medico.id, HorarioMedico.dia_semana == fecha.weekday())
    ]

    inicio_dia = datetime.combine(fecha, datetime.min.time())
    ocupados = [
        (t.fecha_hora, t.fecha_hora + timedelta(minutes=t.duracion))
        for t in db.query(Turno)
        .join(EstadoTurno)
        .filter(
            Turno.id_medicos == medico.id,
            Turno.fecha_hora >= inicio_dia - timedelta(days=1),
            Turno.fecha_hora < inicio_dia + timedelta(days=1),
            EstadoTurno.estado.in_(["pendiente", "aceptado"]),
        )
    ]

    duracion = timedelta(minutes=medico.duracion_turno)
    paso = timedelta(minutes=medico.duracion_turno + medico.margen_turno)
    ahora = ahora or datetime.now()

    libres = []
    for desde, hasta in _bloques(horas):
        turno = inicio_dia + timedelta(hours=desde)
        fin = inicio_dia + timedelta(hours=hasta)
        while turno + duracion <= fin:
            libre = all(turno + duracion <= inicio or turno >= fin for inicio, fin in ocupados)
            if turno > ahora and libre:
                libres.append(turno)
            turno += paso
    return libres
