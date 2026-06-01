from fastapi import FastAPI
from routers import auth_medicos, auth_pacientes

app = FastAPI(title="MediApp API", version="1.0.0")

app.include_router(auth_medicos.router)
app.include_router(auth_pacientes.router)


@app.get("/")
def root():
    return {"message": "MediApp API funcionando"}
