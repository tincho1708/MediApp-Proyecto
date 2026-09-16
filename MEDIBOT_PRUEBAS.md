# MediBot: cómo probarlo

## Arrancar en esta computadora (PowerShell)

Desde la raíz `MediApp-Proyecto`, el Python portátil y las dependencias quedaron
preparados en `.tools/python/` (ignorados por Git):

```powershell
.\.tools\python\python.exe -m uvicorn Back:app --reload
```

En otra terminal, también desde la raíz:

```powershell
cd Front-end/ProyectoVue-MediApp
npm.cmd run dev -- --port 5173 --strictPort
```

Abrí <http://localhost:5173>, iniciá sesión con **correo y contraseña** y entrá a
MediBot desde el panel correspondiente. La API está en <http://localhost:8000/docs>.

## Prueba manual

Usá cuentas y datos de prueba. Para probar pacientes del médico, necesitás un turno
aceptado que los vincule; para disponibilidad, el profesional debe tener horarios cargados.

1. **Como paciente:** «¿Qué especialidades hay?», «Mostrame los médicos»,
   «Mostrame la siguiente página», «Buscá a [nombre completo]» y
   «¿Qué horarios libres tiene en los próximos 7 días?».
2. **Como médico:** «¿Cuántos pacientes tengo?», «Mostrame mis pacientes»,
   «Buscá a [nombre completo de un paciente propio]», «¿Tengo solicitudes pendientes?».
3. **Aislamiento:** como médico, pedí la ficha de alguien que solo atienda otro médico.
   No debe devolver esa ficha. Como paciente, pedí listar pacientes de un médico:
   no tiene esa herramienta disponible.
4. **Nombres repetidos:** si hay dos personas coincidentes, debe pedir aclaración.
   Elegí una y verificá que la ficha corresponda a esa persona.
5. **Historial:** empezá otro chat, reabrí el anterior y seguí conversando. Probá más de
   20 intercambios: el navegador envía solo el nuevo mensaje y el servidor carga los
   últimos 12 mensajes guardados.
6. **Borrado:** borrá una conversación desde el panel. Debe desaparecer solo si el
   servidor confirma que se eliminó. Durante una respuesta, cambiar o borrar chats
   está deshabilitado.

## Alcance

- El paciente puede buscar todos los médicos con correo verificado.
- Las búsquedas de médicos y pacientes tienen páginas de 20, total real y `hay_mas`.
- Un paciente del médico se identifica por tener algún turno aceptado con él.
  Las solicitudes pendientes se consultan aparte y no habilitan su ficha completa.
- La ficha muestra los últimos 15 turnos **con ese médico**, no notas de otros médicos.
- Las búsquedas admiten nombres completos y selección por ID ante coincidencias múltiples.
- Los horarios libres muestran hasta 20 opciones ordenadas por fecha, dentro de
  un rango de 1 a 90 días, descontando turnos pendientes y aceptados.
- MediBot consulta datos; **no reserva, acepta ni cancela turnos**. Para pedir un turno,
  se usa «Reservar Turno».
- Las fechas mantienen la convención UTC del backend existente.

## Configuración

En el `.env` de la raíz, además de la configuración habitual de base, JWT y correo:

```dotenv
GROQ_API_KEY=tu_key
GROQ_MODEL=openai/gpt-oss-20b
```

El modelo anterior `llama-3.3-70b-versatile` devolvió `model_not_found` con la key
configurada. Se comprobó que `openai/gpt-oss-20b` está disponible y completa un
intercambio de herramientas con datos ficticios. La disponibilidad depende de la cuenta;
consultar los [modelos de Groq](https://console.groq.com/docs/models).

En `Front-end/ProyectoVue-MediApp/.env`:

```dotenv
VITE_API_URL=http://localhost:8000
```

En otra computadora, instalar Python y las dependencias en un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn Back:app --reload
```

En el frontend, ejecutar `npm.cmd install` antes de `npm.cmd run dev`.
El Python portátil en `.tools/` es local a esta computadora y no se comparte por Git.

### Tablas

En la base configurada se confirmó la existencia de `medicos`, `pacientes`, `turno`,
`conversacion_medibot` y `mensaje_medibot`; no se modificaron datos reales.

Para una base nueva gestionada con Alembic, aplicar las migraciones pendientes con
`python -m alembic upgrade head` usando el Python del entorno. Si las tablas se
crearon mediante `migracion_medibot.sql`, revisar primero el estado de Alembic:
no ejecutar ambos métodos a ciegas, porque intentan crear las mismas tablas.

## Verificación automatizada

Desde la raíz, en esta computadora:

```powershell
.\.tools\python\python.exe -m unittest discover -s tests -v
```

Las pruebas usan SQLite en memoria y Groq simulado: no consumen la key ni leen o
modifican la base real. Cubren permisos, aislamiento, nombres, paginación, argumentos,
disponibilidad, historial, borrado y errores del proveedor.

Para compilar el frontend:

```powershell
cd Front-end/ProyectoVue-MediApp
npm.cmd run build
```

## Errores habituales

- **Sesión vencida:** volver a iniciar sesión con correo y contraseña.
- **Modelo no disponible:** revisar `GROQ_MODEL` y reiniciar el backend.
- **Key/permisos:** revisar `GROQ_API_KEY` y el acceso al modelo en Groq.
- **Límite de uso:** esperar y revisar la cuota de Groq.
- **Sin pacientes:** comprobar que haya turnos aceptados con ese médico.
- **Sin médicos:** comprobar que sus correos estén verificados.
- **Sin conexión:** comprobar los servidores, `VITE_API_URL` y el puerto 5173.
  Reiniciar Vite tras modificar su `.env`.
