from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_medicos, auth_pacientes, auth_google, medicos, turnos, medibot

app = FastAPI(title="MediApp API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_medicos.router)
app.include_router(auth_pacientes.router)
app.include_router(auth_google.router)
app.include_router(medicos.router)
app.include_router(turnos.router)
app.include_router(medibot.router)


@app.get("/")
def root():
    return {"message": "MediApp API funcionando"}
