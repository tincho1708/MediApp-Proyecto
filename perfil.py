from fastapi import HTTPException


def limpiar_datos(data):
    datos = {campo: (valor.strip() or None) if isinstance(valor, str) else valor for campo, valor in data.model_dump().items()}
    if not datos["nombre"]:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    datos["apellido"] = datos["apellido"] or ""
    return datos
