# MediBot

Asistente de IA de MediApp. Groq (llama-3.3-70b) con tool calling contra la base de datos del proyecto.

## Qué cambió

**Archivos nuevos**

- `routers/medibot.py` — toda la lógica: herramientas, prompts, bucle de tool calling, endpoints
- `migracion_medibot.sql` — las dos tablas del historial

**Archivos modificados**

- `models.py` — se agregaron `ConversacionMediBot` y `MensajeMediBot`
- `schemas.py` — se agregó el bloque `# --- MediBot ---`
- `Back.py` — se registró el router
- `Front-end/.../components/MediBot.vue` — reescrito: el chat funcionando
- `Front-end/.../src/App.vue` — arreglado un import roto (ver abajo)

## Arrancar

### 1. Backend

En el `.env` de la raíz agregá:

```
GROQ_API_KEY=tu_key_de_groq
GROQ_MODEL=llama-3.3-70b-versatile
```

No hace falta instalar nada: la llamada a Groq usa `httpx`, que ya estaba en `requirements.txt`.

Creá las tablas:

```bash
psql "$DATABASE_URL" -f migracion_medibot.sql
```

Levantá la API como siempre:

```bash
uvicorn Back:app --reload
```

Probalo en `http://localhost:8000/docs`, sección **MediBot**.

### 2. Frontend

```bash
cd Front-end/ProyectoVue-MediApp
npm install
npm run dev
```

No hace falta tocar el `.env` del front: ya apunta a `VITE_API_URL=http://localhost:8000`.

## El import roto de App.vue

`App.vue` importaba `./components/chatbot.vue`, un archivo que no existe en el repo. Eso rompía el build entero, no solo MediBot. Ahora importa `./components/MediBot.vue` y le pasa los eventos de navegación de ambos roles.

## Cómo funciona

```
MediBot.vue  ──JWT──>  /medibot/chat  ──>  Groq
                            │
                            └──> tus tablas (turno, medicos, pacientes...)
```

El navegador nunca toca a Groq, así que la key no se puede robar desde el inspector.

El rol sale de `user["tipo"]` del JWT, nunca del body. Según el rol se arma la lista de herramientas, y el modelo solo ve las de su rol.

### Herramientas del médico

| Herramienta | Qué devuelve |
|---|---|
| `listar_mis_pacientes` | Pacientes con turnos aceptados con él |
| `ficha_paciente` | Datos + historial de turnos con las notas clínicas |
| `mi_agenda` | Turnos aceptados de los próximos N días |
| `turnos_pendientes` | Solicitudes sin responder |
| `mis_horarios` | Su configuración de días y horas |
| `buscar_colegas` | Otros profesionales, para derivar |

### Herramientas del paciente

| Herramienta | Qué devuelve |
|---|---|
| `buscar_medicos` | Profesionales por especialidad o nombre, con valoración |
| `detalle_medico` | Ficha completa: reseñas, recomendaciones de colegas, horarios |
| `listar_especialidades` | Todas las especialidades y cuántos profesionales tienen |
| `mis_turnos` | Sus propios turnos y en qué estado están |
| `horarios_libres` | Huecos reales de un profesional, descontando turnos ocupados |

### Las tres capas de aislamiento

1. **El rol sale del token.** Si alguien manda `{"tipo": "medico"}` por Postman con un token de paciente, se ignora.
2. **Las herramientas se filtran por rol** antes de mandárselas al modelo, y se vuelven a validar en `ejecutar_tool` antes de correrlas.
3. **Cada consulta filtra por el id del usuario.** `ficha_paciente` exige que exista un turno aceptado entre ese médico y ese paciente; si no, devuelve "no encontrado" aunque el paciente exista.

Probado: un médico pidiendo la ficha de un paciente que no es suyo recibe "no encontrado", y un paciente pidiendo `ficha_paciente` recibe "no disponible para este tipo de cuenta".

## Probarlo

Como médico:

- ¿Cuántos pacientes tengo?
- Contame de Anahí Liguori
- ¿Cómo viene mi semana?
- ¿Tengo solicitudes sin responder?
- Necesito derivar a alguien a dermatología

Como paciente:

- Necesito un psicólogo
- ¿Qué sabés de Gonzalo?
- ¿Cuándo tiene turnos libres?
- ¿Cuándo es mi próximo turno?

## Si algo falla

| Síntoma | Causa |
|---|---|
| `Falta configurar GROQ_API_KEY` | No está en el `.env`, o no reiniciaste uvicorn |
| 401 en el front | El token venció (`ACCESS_TOKEN_EXPIRE_MINUTES` está en 30 por defecto) |
| `MediBot no pudo procesar la consulta` | Groq rechazó la llamada. El detalle sale por consola del backend |
| Responde pero dice que no encuentra pacientes | Los turnos tienen que estar en estado `aceptado`, no `pendiente` |
| Error de CORS | El front tiene que correr en `localhost:5173` o `localhost:3000` |

## Detalles a tener en cuenta

Las fechas se guardan con `datetime.utcnow()`, igual que el resto del proyecto. Si tus turnos se ven corridos tres horas, es eso y afecta a toda la app, no solo a MediBot.

`MAX_HISTORIAL = 12` limita cuántos mensajes previos se le mandan al modelo. Si lo subís, cada mensaje sale más caro en tokens.

MediBot maneja datos de salud. Para el proyecto está bien así, pero si algún día atiende gente de verdad hacen falta consentimiento explícito, registro de auditoría de accesos y un acuerdo de tratamiento de datos con Groq. En Argentina los datos de salud son categoría sensible según la Ley 25.326.
