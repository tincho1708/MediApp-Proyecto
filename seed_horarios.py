from database import SessionLocal
from models import Medico, HorarioMedico

db = SessionLocal()

DIAS = list(range(5))   # lunes a viernes
HORAS = list(range(9, 17))  # 9:00 a 16:00

try:
    medicos = db.query(Medico).all()
    for medico in medicos:
        existentes = db.query(HorarioMedico).filter(HorarioMedico.id_medico == medico.id).count()
        if existentes > 0:
            print(f"Ya tiene horarios: {medico.nombre} {medico.apellido}")
            continue
        for dia in DIAS:
            for hora in HORAS:
                db.add(HorarioMedico(id_medico=medico.id, dia_semana=dia, hora=hora))
        print(f"Horarios creados para: {medico.nombre} {medico.apellido}")
    db.commit()
    print("\nListo.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
