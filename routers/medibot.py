"""
MediBot — el asistente de IA de MediApp.

Cómo funciona:
  1. El frontend manda el historial del chat + el token JWT.
  2. Acá se lee el `tipo` del token (medico | paciente). El frontend NUNCA
     decide el rol: si alguien manda {"tipo": "medico"} en el body, se ignora.
  3. Según el rol se le ofrecen al modelo unas herramientas u otras.
     Un paciente ni siquiera ve que existe `ficha_paciente`.
  4. El modelo pide ejecutar herramientas, nosotros las corremos contra la
     base filtrando SIEMPRE por el id del usuario, y le devolvemos el
     resultado. Repetimos hasta que responde en texto.
"""

import os
import json
import datetime
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user
from models import (
    ConversacionMediBot,
    Especialidad,
    EstadoTurno,
    HorarioMedico,
    MensajeMediBot,
    Medico,
    Paciente,
    Recomienda,
    Resena,
    Turno,
)
from schemas import (
    ConversacionResponse,
    MediBotRequest,
    MediBotResponse,
    MensajeMediBotResponse,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

MAX_VUELTAS = 5          # tope de rondas de herramientas por mensaje
MAX_HISTORIAL = 12       # cuántos mensajes previos se le mandan al modelo

router = APIRouter(prefix="/medibot", tags=["MediBot"])

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


# =====================================================================
# DEFINICIÓN DE HERRAMIENTAS
# =====================================================================

TOOLS_MEDICO = [
    {
        "type": "function",
        "function": {
            "name": "listar_mis_pacientes",
            "description": (
                "Lista los pacientes que tienen o tuvieron turnos aceptados con este médico. "
                "Usar cuando pregunta por 'mis pacientes', cuántos tiene, o quiere un panorama."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "busqueda": {
                        "type": "string",
                        "description": "Filtro opcional por nombre o apellido.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ficha_paciente",
            "description": (
                "Datos de un paciente concreto del médico y su historial de turnos con las notas "
                "clínicas cargadas. Usar cuando menciona a un paciente por nombre."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre o apellido del paciente.",
                    }
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mi_agenda",
            "description": (
                "Turnos aceptados del médico de acá en adelante. Usar para 'qué tengo hoy', "
                "'cómo viene la semana', 'próximos turnos'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dias": {
                        "type": "integer",
                        "description": "Cuántos días hacia adelante mirar. Por defecto 7.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "turnos_pendientes",
            "description": "Solicitudes de turno que el médico todavía no aceptó ni rechazó.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mis_horarios",
            "description": "Los días y horas en que este médico atiende, según su configuración.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_colegas",
            "description": (
                "Busca otros profesionales de MediApp por especialidad o nombre. "
                "Sirve para derivar un paciente a un colega."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "especialidad": {"type": "string", "description": "Ej: 'cardiología'."},
                    "nombre": {"type": "string", "description": "Nombre o apellido."},
                },
            },
        },
    },
]

TOOLS_PACIENTE = [
    {
        "type": "function",
        "function": {
            "name": "buscar_medicos",
            "description": (
                "Busca profesionales en MediApp por especialidad o por nombre. Usar siempre que "
                "el usuario pida una recomendación o pregunte por profesionales disponibles."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "especialidad": {
                        "type": "string",
                        "description": "Ej: 'psicología', 'dermatología', 'clínica médica'.",
                    },
                    "nombre": {"type": "string", "description": "Nombre o apellido del profesional."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detalle_medico",
            "description": (
                "Ficha completa de un profesional: especialidades, valoración de los pacientes, "
                "cuántos colegas lo recomiendan y sus horarios de atención."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre o apellido del profesional."}
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_especialidades",
            "description": "Todas las especialidades cargadas en MediApp y cuántos profesionales tiene cada una.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mis_turnos",
            "description": "Los turnos del usuario: con qué profesional, cuándo y en qué estado están.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "horarios_libres",
            "description": (
                "Horarios disponibles de un profesional en los próximos días, ya descontando "
                "los turnos ocupados. Usar cuando el usuario quiere sacar un turno."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del profesional."},
                    "dias": {"type": "integer", "description": "Cuántos días mirar. Por defecto 14."},
                },
                "required": ["nombre"],
            },
        },
    },
]


# =====================================================================
# PROMPTS
# =====================================================================

def prompt_sistema(tipo: str, nombre: str) -> str:
    hoy = datetime.datetime.now().strftime("%A %d/%m/%Y")
    base = (
        f"Sos MediBot, el asistente de MediApp. Hablás en español rioplatense, breve y claro. "
        f"Hoy es {hoy}. Estás hablando con {nombre}.\n\n"
        "Reglas que no se rompen:\n"
        "- Solo sabés lo que te devuelven las herramientas. Si una herramienta viene vacía, decí "
        "que no encontraste el dato. Nunca inventes nombres, fechas, matrículas ni resultados.\n"
        "- Antes de hablar de cualquier persona o turno, consultá la herramienta correspondiente.\n"
        "- Listas de personas o turnos: viñetas cortas, no tablas gigantes.\n"
        "- No repitas datos sensibles que no hagan falta para responder."
    )

    if tipo == "medico":
        return base + (
            f"\n\n{nombre} es profesional de la salud y usa MediApp para su consultorio. Podés "
            "consultar sus pacientes, la ficha e historial de cada uno, su agenda, las solicitudes "
            "pendientes y sus horarios de atención.\n"
            "Ayudalo a organizarse: resumir la agenda, recordar el historial de un paciente antes "
            "de una consulta, ver qué solicitudes tiene sin responder. Podés conversar sobre "
            "criterios clínicos generales como lo haría un colega, pero no emitís diagnósticos ni "
            "indicás tratamientos: la decisión clínica es suya."
        )

    return base + (
        f"\n\n{nombre} es un paciente que busca atención. Tu trabajo principal es ayudarlo a "
        "encontrar el profesional adecuado en MediApp y contarle sobre ellos: especialidad, "
        "valoración, recomendaciones de colegas, horarios libres. También podés mostrarle sus "
        "propios turnos.\n"
        "Si describe un síntoma, no diagnostiques ni sugieras medicación. Orientalo sobre a qué "
        "especialidad conviene consultar y buscale profesionales de esa especialidad. Si lo que "
        "cuenta suena urgente o grave, decile que vaya a una guardia o llame al 107 antes que nada."
    )


# =====================================================================
# HELPERS
# =====================================================================

def _fecha(dt: datetime.datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")


def _nombre_completo(p) -> str:
    return f"{p.nombre} {p.apellido}".strip()


def _valoracion(db: Session, medico_id: int) -> Optional[float]:
    prom = db.query(func.avg(Resena.estrellas)).filter(Resena.id_medico == medico_id).scalar()
    return round(float(prom), 1) if prom is not None else None


def _medico_resumen(db: Session, m: Medico) -> dict:
    return {
        "id": m.id,
        "nombre": _nombre_completo(m),
        "especialidades": [e.nombre_especialidad for e in m.especialidades],
        "valoracion": _valoracion(db, m.id),
        "recomendaciones_de_colegas": db.query(Recomienda)
        .filter(Recomienda.id_medico_recomendado == m.id)
        .count(),
    }


def _buscar_medico_por_nombre(db: Session, texto: str) -> Optional[Medico]:
    like = f"%{texto.strip()}%"
    return (
        db.query(Medico)
        .options(joinedload(Medico.especialidades))
        .filter(
            Medico.email_verificado == True,  # noqa: E712
            (Medico.nombre.ilike(like)) | (Medico.apellido.ilike(like)),
        )
        .first()
    )


def _estado_id(db: Session, nombre: str) -> Optional[int]:
    e = db.query(EstadoTurno).filter(EstadoTurno.estado == nombre).first()
    return e.id if e else None


# =====================================================================
# EJECUCIÓN DE HERRAMIENTAS
# =====================================================================

def ejecutar_tool(nombre: str, args: dict, db: Session, user_id: int, tipo: str) -> Any:
    # Cinturón extra: si el modelo alucina una herramienta del otro rol, se corta acá.
    permitidas = [t["function"]["name"] for t in (TOOLS_MEDICO if tipo == "medico" else TOOLS_PACIENTE)]
    if nombre not in permitidas:
        return {"error": "Esa consulta no está disponible para este tipo de cuenta."}

    # ---------------------------- MÉDICO ----------------------------
    if nombre == "listar_mis_pacientes":
        id_aceptado = _estado_id(db, "aceptado")
        q = (
            db.query(Paciente)
            .join(Turno, Turno.id_pacientes == Paciente.id)
            .filter(Turno.id_medicos == user_id, Turno.id_estado == id_aceptado)
        )
        busqueda = (args.get("busqueda") or "").strip()
        if busqueda:
            like = f"%{busqueda}%"
            q = q.filter((Paciente.nombre.ilike(like)) | (Paciente.apellido.ilike(like)))

        pacientes = q.distinct().order_by(Paciente.apellido, Paciente.nombre).all()
        return {
            "total": len(pacientes),
            "pacientes": [
                {
                    "nombre": _nombre_completo(p),
                    "telefono": p.telefono,
                    "turnos_conmigo": db.query(Turno)
                    .filter(Turno.id_pacientes == p.id, Turno.id_medicos == user_id)
                    .count(),
                }
                for p in pacientes
            ],
        }

    if nombre == "ficha_paciente":
        texto = (args.get("nombre") or "").strip()
        like = f"%{texto}%"
        id_aceptado = _estado_id(db, "aceptado")

        # El paciente tiene que tener al menos un turno aceptado con ESTE médico.
        paciente = (
            db.query(Paciente)
            .join(Turno, Turno.id_pacientes == Paciente.id)
            .filter(
                Turno.id_medicos == user_id,
                Turno.id_estado == id_aceptado,
                (Paciente.nombre.ilike(like)) | (Paciente.apellido.ilike(like)),
            )
            .first()
        )
        if not paciente:
            return {
                "encontrado": False,
                "mensaje": "No hay ningún paciente con ese nombre entre los tuyos.",
            }

        turnos = (
            db.query(Turno)
            .options(joinedload(Turno.estado))
            .filter(Turno.id_pacientes == paciente.id, Turno.id_medicos == user_id)
            .order_by(Turno.fecha_hora.desc())
            .limit(15)
            .all()
        )
        return {
            "encontrado": True,
            "paciente": {
                "nombre": _nombre_completo(paciente),
                "telefono": paciente.telefono,
                "mail": paciente.mail,
            },
            "historial": [
                {
                    "fecha": _fecha(t.fecha_hora),
                    "estado": t.estado.estado,
                    "notas": t.notas or "sin notas",
                }
                for t in turnos
            ],
        }

    if nombre == "mi_agenda":
        dias = int(args.get("dias") or 7)
        ahora = datetime.datetime.utcnow()
        hasta = ahora + datetime.timedelta(days=dias)
        id_aceptado = _estado_id(db, "aceptado")

        turnos = (
            db.query(Turno)
            .options(joinedload(Turno.paciente), joinedload(Turno.estado))
            .filter(
                Turno.id_medicos == user_id,
                Turno.id_estado == id_aceptado,
                Turno.fecha_hora >= ahora,
                Turno.fecha_hora <= hasta,
            )
            .order_by(Turno.fecha_hora)
            .all()
        )
        return {
            "rango_dias": dias,
            "total": len(turnos),
            "turnos": [
                {
                    "fecha": _fecha(t.fecha_hora),
                    "dia": DIAS[t.fecha_hora.weekday()],
                    "paciente": _nombre_completo(t.paciente),
                    "notas": t.notas,
                }
                for t in turnos
            ],
        }

    if nombre == "turnos_pendientes":
        id_pendiente = _estado_id(db, "pendiente")
        turnos = (
            db.query(Turno)
            .options(joinedload(Turno.paciente))
            .filter(Turno.id_medicos == user_id, Turno.id_estado == id_pendiente)
            .order_by(Turno.fecha_hora)
            .all()
        )
        return {
            "total": len(turnos),
            "solicitudes": [
                {
                    "fecha_pedida": _fecha(t.fecha_hora),
                    "paciente": _nombre_completo(t.paciente),
                    "motivo": t.notas,
                    "solicitado_el": _fecha(t.creado_en),
                }
                for t in turnos
            ],
        }

    if nombre == "mis_horarios":
        horarios = (
            db.query(HorarioMedico)
            .filter(HorarioMedico.id_medico == user_id)
            .order_by(HorarioMedico.dia_semana, HorarioMedico.hora)
            .all()
        )
        agrupado: dict[str, list[str]] = {}
        for h in horarios:
            agrupado.setdefault(DIAS[h.dia_semana], []).append(f"{h.hora}:00")
        return {"horarios": agrupado or "No tenés horarios cargados todavía."}

    if nombre == "buscar_colegas":
        return _buscar_medicos(db, args, excluir_id=user_id)

    # --------------------------- PACIENTE ---------------------------
    if nombre == "buscar_medicos":
        return _buscar_medicos(db, args)

    if nombre == "detalle_medico":
        medico = _buscar_medico_por_nombre(db, args.get("nombre") or "")
        if not medico:
            return {"encontrado": False, "mensaje": "No hay un profesional con ese nombre en MediApp."}

        horarios = (
            db.query(HorarioMedico)
            .filter(HorarioMedico.id_medico == medico.id)
            .order_by(HorarioMedico.dia_semana, HorarioMedico.hora)
            .all()
        )
        agrupado: dict[str, list[str]] = {}
        for h in horarios:
            agrupado.setdefault(DIAS[h.dia_semana], []).append(f"{h.hora}:00")

        datos = _medico_resumen(db, medico)
        datos["telefono"] = medico.telefono
        datos["mail"] = medico.mail
        datos["atiende"] = agrupado or "Sin horarios cargados."
        datos["resenas_recibidas"] = db.query(Resena).filter(Resena.id_medico == medico.id).count()
        return {"encontrado": True, "profesional": datos}

    if nombre == "listar_especialidades":
        filas = (
            db.query(Especialidad.nombre_especialidad, func.count(Medico.id))
            .outerjoin(Especialidad.medicos)
            .group_by(Especialidad.nombre_especialidad)
            .order_by(func.count(Medico.id).desc())
            .all()
        )
        return {"especialidades": [{"nombre": n, "profesionales": c} for n, c in filas]}

    if nombre == "mis_turnos":
        turnos = (
            db.query(Turno)
            .options(
                joinedload(Turno.medico).joinedload(Medico.especialidades),
                joinedload(Turno.estado),
            )
            .filter(Turno.id_pacientes == user_id)
            .order_by(Turno.fecha_hora.desc())
            .limit(15)
            .all()
        )
        return {
            "total": len(turnos),
            "turnos": [
                {
                    "fecha": _fecha(t.fecha_hora),
                    "profesional": _nombre_completo(t.medico),
                    "especialidades": [e.nombre_especialidad for e in t.medico.especialidades],
                    "estado": t.estado.estado,
                    "notas": t.notas,
                }
                for t in turnos
            ],
        }

    if nombre == "horarios_libres":
        medico = _buscar_medico_por_nombre(db, args.get("nombre") or "")
        if not medico:
            return {"encontrado": False, "mensaje": "No hay un profesional con ese nombre en MediApp."}

        dias = int(args.get("dias") or 14)
        ahora = datetime.datetime.utcnow()
        hasta = ahora + datetime.timedelta(days=dias)

        horarios = db.query(HorarioMedico).filter(HorarioMedico.id_medico == medico.id).all()
        if not horarios:
            return {"encontrado": True, "profesional": _nombre_completo(medico), "libres": [], "mensaje": "Este profesional no tiene horarios cargados."}

        ocupados = {
            t.fecha_hora.replace(minute=0, second=0, microsecond=0)
            for t in db.query(Turno)
            .join(EstadoTurno)
            .filter(
                Turno.id_medicos == medico.id,
                Turno.fecha_hora >= ahora,
                Turno.fecha_hora <= hasta,
                EstadoTurno.estado.in_(["pendiente", "aceptado"]),
            )
            .all()
        }

        libres = []
        dia = ahora.replace(minute=0, second=0, microsecond=0)
        while dia <= hasta and len(libres) < 20:
            for h in horarios:
                if h.dia_semana != dia.weekday():
                    continue
                slot = dia.replace(hour=h.hora)
                if slot > ahora and slot not in ocupados:
                    libres.append(f"{DIAS[slot.weekday()]} {_fecha(slot)}")
            dia += datetime.timedelta(days=1)

        return {
            "encontrado": True,
            "profesional": _nombre_completo(medico),
            "libres": sorted(set(libres))[:20],
        }

    return {"error": "Herramienta desconocida."}


def _buscar_medicos(db: Session, args: dict, excluir_id: Optional[int] = None) -> dict:
    q = db.query(Medico).options(joinedload(Medico.especialidades)).filter(
        Medico.email_verificado == True  # noqa: E712
    )
    if excluir_id:
        q = q.filter(Medico.id != excluir_id)

    especialidad = (args.get("especialidad") or "").strip()
    if especialidad:
        q = q.filter(Medico.especialidades.any(Especialidad.nombre_especialidad.ilike(f"%{especialidad}%")))

    nombre = (args.get("nombre") or "").strip()
    if nombre:
        like = f"%{nombre}%"
        q = q.filter((Medico.nombre.ilike(like)) | (Medico.apellido.ilike(like)))

    medicos = q.order_by(Medico.apellido, Medico.nombre).limit(8).all()
    return {"total": len(medicos), "profesionales": [_medico_resumen(db, m) for m in medicos]}


# =====================================================================
# LLAMADA A GROQ
# =====================================================================

def llamar_groq(messages: list, tools: list) -> dict:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Falta configurar GROQ_API_KEY en el .env")

    try:
        r = httpx.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.4,
                "max_tokens": 1024,
            },
            timeout=45.0,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="MediBot no está disponible en este momento.")

    if r.status_code != 200:
        print(f"[MediBot] Groq respondió {r.status_code}: {r.text}")
        raise HTTPException(status_code=502, detail="MediBot no pudo procesar la consulta.")

    return r.json()


# =====================================================================
# ENDPOINTS
# =====================================================================

@router.post("/chat", response_model=MediBotResponse)
def chat(
    data: MediBotRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = int(user["sub"])
    tipo = user["tipo"]  # del token, no del body

    if tipo == "medico":
        persona = db.query(Medico).filter(Medico.id == user_id).first()
        tools = TOOLS_MEDICO
    else:
        persona = db.query(Paciente).filter(Paciente.id == user_id).first()
        tools = TOOLS_PACIENTE

    if not persona:
        raise HTTPException(status_code=404, detail="No encontramos tu cuenta.")

    historial = [m.model_dump() for m in data.messages][-MAX_HISTORIAL:]
    if not historial or historial[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="Falta el mensaje del usuario.")

    mensaje_usuario = historial[-1]["content"]

    messages: list[dict] = [{"role": "system", "content": prompt_sistema(tipo, persona.nombre)}]
    messages.extend(historial)

    respuesta_final = ""
    herramientas_usadas: list[str] = []

    for _ in range(MAX_VUELTAS):
        completion = llamar_groq(messages, tools)
        msg = completion["choices"][0]["message"]
        messages.append(msg)

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            respuesta_final = msg.get("content") or ""
            break

        for call in tool_calls:
            fn = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}

            herramientas_usadas.append(fn)
            resultado = ejecutar_tool(fn, args, db, user_id, tipo)

            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "name": fn,
                "content": json.dumps(resultado, ensure_ascii=False, default=str),
            })

    if not respuesta_final:
        respuesta_final = "No pude completar la consulta. ¿Probamos preguntándolo de otra forma?"

    # --- Guardar la conversación ---
    conversacion_id = data.conversacion_id
    if conversacion_id:
        conv = (
            db.query(ConversacionMediBot)
            .filter(
                ConversacionMediBot.id == conversacion_id,
                ConversacionMediBot.usuario_id == user_id,
                ConversacionMediBot.tipo_usuario == tipo,
            )
            .first()
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada.")
    else:
        conv = ConversacionMediBot(
            usuario_id=user_id,
            tipo_usuario=tipo,
            titulo=mensaje_usuario[:60],
        )
        db.add(conv)
        db.flush()

    db.add(MensajeMediBot(id_conversacion=conv.id, rol="user", contenido=mensaje_usuario))
    db.add(MensajeMediBot(id_conversacion=conv.id, rol="assistant", contenido=respuesta_final))
    db.commit()

    return MediBotResponse(
        respuesta=respuesta_final,
        conversacion_id=conv.id,
        herramientas_usadas=herramientas_usadas,
    )


@router.get("/conversaciones", response_model=list[ConversacionResponse])
def listar_conversaciones(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return (
        db.query(ConversacionMediBot)
        .filter(
            ConversacionMediBot.usuario_id == int(user["sub"]),
            ConversacionMediBot.tipo_usuario == user["tipo"],
        )
        .order_by(ConversacionMediBot.creado_en.desc())
        .limit(30)
        .all()
    )


@router.get("/conversaciones/{conversacion_id}", response_model=list[MensajeMediBotResponse])
def ver_conversacion(
    conversacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    conv = (
        db.query(ConversacionMediBot)
        .filter(
            ConversacionMediBot.id == conversacion_id,
            ConversacionMediBot.usuario_id == int(user["sub"]),
            ConversacionMediBot.tipo_usuario == user["tipo"],
        )
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada.")

    return (
        db.query(MensajeMediBot)
        .filter(MensajeMediBot.id_conversacion == conversacion_id)
        .order_by(MensajeMediBot.creado_en)
        .all()
    )


@router.delete("/conversaciones/{conversacion_id}", status_code=204)
def borrar_conversacion(
    conversacion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    conv = (
        db.query(ConversacionMediBot)
        .filter(
            ConversacionMediBot.id == conversacion_id,
            ConversacionMediBot.usuario_id == int(user["sub"]),
            ConversacionMediBot.tipo_usuario == user["tipo"],
        )
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada.")
    db.delete(conv)
    db.commit()
