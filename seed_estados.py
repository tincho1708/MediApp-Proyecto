from database import SessionLocal
from models import EstadoTurno

db = SessionLocal()

estados = ["pendiente", "aceptado", "rechazado", "cancelado"]

try:
    for nombre in estados:
        existe = db.query(EstadoTurno).filter(EstadoTurno.estado == nombre).first()
        if not existe:
            db.add(EstadoTurno(estado=nombre))
            print(f"Estado creado: {nombre}")
        else:
            print(f"Ya existe: {nombre}")
    db.commit()
    print("\nListo.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
