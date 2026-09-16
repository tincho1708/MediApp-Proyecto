from database import SessionLocal
from models import Medico, Paciente, Especialidad, HorarioMedico
from auth_utils import hash_password

db = SessionLocal()

medicos_data = [
    {"nombre": "Carlos", "apellido": "García", "mail": "carlos.garcia@mediapp.com", "especialidad_ids": [1]},
    {"nombre": "Laura", "apellido": "Martínez", "mail": "laura.martinez@mediapp.com", "especialidad_ids": [2]},
]

pacientes_data = [
    {"nombre": "Juan", "apellido": "López", "mail": "juan.lopez@mediapp.com"},
    {"nombre": "Ana", "apellido": "Torres", "mail": "ana.torres@mediapp.com"},
]

try:
    for data in medicos_data:
        existe = db.query(Medico).filter(Medico.mail == data["mail"]).first()
        if existe:
            print(f"Ya existe: {data['mail']}")
            continue

        medico = Medico(
            nombre=data["nombre"],
            apellido=data["apellido"],
            mail=data["mail"],
            password_hash=hash_password("Test1234"),
            email_verificado=True,
        )
        db.add(medico)
        db.flush()

        especialidades = db.query(Especialidad).filter(
            Especialidad.id_especialidad.in_(data["especialidad_ids"])
        ).all()
        medico.especialidades = especialidades

        for dia in range(5):
            for hora in range(9, 17):
                db.add(HorarioMedico(id_medico=medico.id, dia_semana=dia, hora=hora))

        print(f"Médico creado: {data['mail']}")

    for data in pacientes_data:
        existe = db.query(Paciente).filter(Paciente.mail == data["mail"]).first()
        if existe:
            print(f"Ya existe: {data['mail']}")
            continue

        paciente = Paciente(
            nombre=data["nombre"],
            apellido=data["apellido"],
            mail=data["mail"],
            password_hash=hash_password("Test1234"),
            email_verificado=True,
        )
        db.add(paciente)
        print(f"Paciente creado: {data['mail']}")

    db.commit()
    print("\nListo. Todos los usuarios tienen contraseña: Test1234")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
