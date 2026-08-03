from database import SessionLocal
from models import Medico, Paciente
from auth_utils import hash_password

db = SessionLocal()

medicos = [
    Medico(
        nombre="Carlos",
        apellido="García",
        mail="carlos.garcia@mediapp.com",
        password_hash=hash_password("Test1234"),
        especialidad_id=1,
        email_verificado=True,
    ),
    Medico(
        nombre="Laura",
        apellido="Martínez",
        mail="laura.martinez@mediapp.com",
        password_hash=hash_password("Test1234"),
        especialidad_id=2,
        email_verificado=True,
    ),
]

pacientes = [
    Paciente(
        nombre="Juan",
        apellido="López",
        mail="juan.lopez@mediapp.com",
        password_hash=hash_password("Test1234"),
        email_verificado=True,
    ),
    Paciente(
        nombre="Ana",
        apellido="Torres",
        mail="ana.torres@mediapp.com",
        password_hash=hash_password("Test1234"),
        email_verificado=True,
    ),
]

try:
    for m in medicos:
        existe = db.query(Medico).filter(Medico.mail == m.mail).first()
        if not existe:
            db.add(m)
            print(f"Médico creado: {m.mail}")
        else:
            print(f"Ya existe: {m.mail}")

    for p in pacientes:
        existe = db.query(Paciente).filter(Paciente.mail == p.mail).first()
        if not existe:
            db.add(p)
            print(f"Paciente creado: {p.mail}")
        else:
            print(f"Ya existe: {p.mail}")

    db.commit()
    print("\nListo. Todos los usuarios tienen contraseña: Test1234")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
