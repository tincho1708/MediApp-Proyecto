<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits([
  'ir-a-profesionales',
  'ir-a-bienvenida',
  'ir-a-principal-usuario',
  'ir-a-chatbot',
  'ir-a-calendario-usuario',
  'ir-a-reservar-turno',
  'ir-a-mi-usuario-paciente',
  'ir-a-notificaciones',
])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Turno = {
  id_turno: number
  fecha_hora: string
  estado: { estado: string }
  medico: {
    nombre: string
    apellido: string
    especialidades: { nombre_especialidad: string }[]
  }
}

const turnos = ref<Turno[]>([])
const cargandoTurnos = ref(true)
const errorTurnos = ref('')

const proximosTurnos = computed(() => {
  const ahora = Date.now()
  return turnos.value
    .filter((t) => t.estado?.estado === 'aceptado' && new Date(t.fecha_hora).getTime() >= ahora)
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
    .slice(0, 4)
})

async function cargarTurnos(silencioso = false) {
  if (!silencioso) {
    cargandoTurnos.value = true
    errorTurnos.value = ''
  }
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) throw new Error()
    turnos.value = await res.json()
  } catch {
    if (!silencioso) errorTurnos.value = 'No se pudieron cargar los turnos.'
  } finally {
    if (!silencioso) cargandoTurnos.value = false
  }
}

onMounted(() => cargarTurnos())

let intervaloTurnos: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  intervaloTurnos = setInterval(() => cargarTurnos(true), 6000)
})
onBeforeUnmount(() => {
  if (intervaloTurnos !== undefined) clearInterval(intervaloTurnos)
})

const mesesAbrev = [
  'ENE',
  'FEB',
  'MAR',
  'ABR',
  'MAY',
  'JUN',
  'JUL',
  'AGO',
  'SEP',
  'OCT',
  'NOV',
  'DIC',
]

function diaNumero(fechaHora: string) {
  return new Date(fechaHora).getDate()
}
function mesAbrev(fechaHora: string) {
  return mesesAbrev[new Date(fechaHora).getMonth()]
}
function formatearHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}
function especialidadTurno(t: Turno) {
  const especialidad = t.medico.especialidades[0]?.nombre_especialidad
  if (especialidad)
    return especialidad.charAt(0).toUpperCase() + especialidad.slice(1).toLowerCase()
  return 'Consulta'
}

const hoy = new Date()
const mesActual = ref(hoy.getMonth())
const añoActual = ref(hoy.getFullYear())

const nombresMes = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

function mesAnterior() {
  if (mesActual.value === 0) {
    mesActual.value = 11
    añoActual.value--
  } else {
    mesActual.value--
  }
}

function mesSiguiente() {
  if (mesActual.value === 11) {
    mesActual.value = 0
    añoActual.value++
  } else {
    mesActual.value++
  }
}

const diasConTurno = computed(() => {
  const hoyInicio = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate()).getTime()
  const set = new Set<number>()
  for (const t of turnos.value) {
    if (t.estado?.estado !== 'aceptado') continue
    const f = new Date(t.fecha_hora)
    const fInicio = new Date(f.getFullYear(), f.getMonth(), f.getDate()).getTime()
    if (fInicio < hoyInicio) continue
    if (f.getMonth() === mesActual.value && f.getFullYear() === añoActual.value) {
      set.add(f.getDate())
    }
  }
  return set
})

const celdas = computed(() => {
  const ultimoDia = new Date(añoActual.value, mesActual.value + 1, 0).getDate()
  const primerDia = new Date(añoActual.value, mesActual.value, 1).getDay()
  const offset = (primerDia + 6) % 7
  const resultado = []

  for (let i = 0; i < offset; i++) {
    resultado.push({ otroMes: true })
  }

  for (let d = 1; d <= ultimoDia; d++) {
    resultado.push({
      dia: d,
      hoy:
        d === hoy.getDate() &&
        mesActual.value === hoy.getMonth() &&
        añoActual.value === hoy.getFullYear(),
      conTurno: diasConTurno.value.has(d),
    })
  }

  let siguiente = 1
  while (resultado.length % 7 !== 0) {
    resultado.push({ dia: siguiente, otroMes: true })
    siguiente++
  }

  return resultado
})
</script>

<template>
  <div>
    <div class="navbar">
      <button @click="emit('ir-a-principal-usuario')">
        <div class="navbar-logo" style="cursor: pointer">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-reservar-turno')">
          Reservar turno<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-chatbot')">
          MediBot<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-profesionales')">
          Profesionales<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-notificaciones')">
          Notificaciones<span v-if="conteoNoLeidas > 0" class="campoo-punto"></span
          ><span class="campoo-indicador"></span>
        </button>
      </div>

      <div class="navbar-usuario-zona">
        <div class="navbar-divisor"></div>
        <button class="navbar-usuario" @click.stop="esta = !esta">
          <div class="navbar-usuario-avatar">{{ nombreUsuario.charAt(0).toUpperCase() }}</div>
          <div class="navbar-usuario-info">
            <span class="navbar-usuario-nombre">{{ nombreUsuario }}</span>
            <span class="navbar-usuario-rol">Mi cuenta</span>
          </div>
          <svg style="width: 1rem; height: 1rem" class="navbar-usuario-chevron" :class="{ 'navbar-usuario-chevron-abierta': esta }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div :class="['barra-desplegable', { 'barra-abierta': esta }]" @click.stop>
          <div class="dropdown-header">
            <div class="dropdown-nombre">{{ nombreUsuario }}</div>
            <div class="dropdown-rol">Cuenta de paciente</div>
          </div>
          <div class="dropdown-divisor"></div>

          <button href="#" @click="emit('ir-a-mi-usuario-paciente')">
            <div class="dropdown-item dropdown-item-destacado">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
              Configuración
            </div>
          </button>

          <button href="#" @click="emit('ir-a-bienvenida')">
            <div class="dropdown-item dropdown-item-danger">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" x2="9" y1="12" y2="12" />
              </svg>
              Cerrar sesión
            </div>
          </button>
        </div>
      </div>
    </div>

    <div class="pu-contenido">
      <div class="pu-encabezado">
        <div>
          <div class="pu-titulo-bienvenida">Bienvenido, {{ nombreUsuario }}</div>
          <p class="pu-subtitulo-bienvenida">Tus turnos y accesos, en un solo lugar.</p>
        </div>
        <button class="pu-boton-reservar" @click="emit('ir-a-reservar-turno')">
          <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Reservar turno
        </button>
      </div>

      <div class="pu-main-layout">
        <div class="pu-columna-izquierda">
          <div class="pu-tarjeta pu-tarjeta-turnos">
            <div class="pu-tarjeta-turnos-header">
              <svg style="width: 1.375rem; height: 1.375rem" viewBox="0 0 24 24" fill="none" stroke="#3D6FC2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="5" width="18" height="16" rx="2" />
                <path d="M16 3v4M8 3v4M3 10h18" />
              </svg>
              <span class="pu-tarjeta-titulo">Próximos turnos</span>
              <span class="pu-badge-contador">{{ proximosTurnos.length }}</span>
            </div>

            <p v-if="cargandoTurnos" class="pu-estado-turnos">Cargando turnos...</p>
            <p v-else-if="errorTurnos" class="pu-estado-turnos pu-error">{{ errorTurnos }}</p>
            <p v-else-if="!proximosTurnos.length" class="pu-estado-turnos">
              No tenés turnos próximos.
            </p>

            <div v-else class="pu-lista-turnos">
              <div v-for="t in proximosTurnos" :key="t.id_turno" class="pu-fila-turno" @click="emit('ir-a-calendario-usuario', t.fecha_hora)">
                <div class="pu-fecha-badge">
                  <span class="pu-fecha-dia">{{ diaNumero(t.fecha_hora) }}</span>
                  <span class="pu-fecha-mes">{{ mesAbrev(t.fecha_hora) }}</span>
                </div>

                <div class="pu-fila-turno-info">
                  <div class="pu-fila-turno-columna">
                    <span class="pu-fila-turno-etiqueta">Tipo de turno</span>
                    <span class="pu-fila-turno-valor">{{ especialidadTurno(t) }}</span>
                  </div>
                  <div class="pu-fila-turno-columna">
                    <span class="pu-fila-turno-etiqueta">Profesional</span>
                    <span class="pu-fila-turno-valor">{{ t.medico.nombre }} {{ t.medico.apellido }}</span>
                  </div>
                  <div class="pu-fila-turno-columna">
                    <span class="pu-fila-turno-etiqueta">Horario</span>
                    <span class="pu-fila-turno-valor pu-fila-turno-reloj">
                      <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="9" />
                        <path d="M12 7v5l3 3" />
                      </svg>
                      {{ formatearHora(t.fecha_hora) }}
                    </span>
                  </div>
                </div>

                <svg class="pu-chevron" style="width: 1.125rem; height: 1.125rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 6l6 6-6 6" />
                </svg>
              </div>
            </div>

            <div class="pu-tarjeta-turnos-footer">
              <span>Consultá los detalles de cada turno.</span>
              <a href="#" class="pu-enlace" @click.prevent="emit('ir-a-calendario-usuario')"
                >Ver todos mis turnos →</a
              >
            </div>
          </div>

          <div class="pu-fila-tarjetas-chicas">
            <div class="pu-tarjeta pu-tarjeta-chica">
              <div class="pu-tarjeta-chica-titulo">Encontrá un profesional</div>
              <p class="pu-tarjeta-chica-desc">Buscá profesionales y elegí con quién atenderte.</p>
              <a href="#" class="pu-enlace" @click.prevent="emit('ir-a-profesionales')"
                >Buscar profesionales →</a
              >
            </div>
            <div class="pu-tarjeta pu-tarjeta-chica">
              <div class="pu-tarjeta-chica-titulo">Conversá con MediBot</div>
              <p class="pu-tarjeta-chica-desc">Hacé una consulta o pedí ayuda para usar MediApp.</p>
              <a href="#" class="pu-enlace" @click.prevent="emit('ir-a-chatbot')"
                >Abrir MediBot →</a
              >
            </div>
          </div>
        </div>

        <div class="pu-columna-derecha">
          <div class="pu-tarjeta pu-calendario">
            <div class="pu-cal-header">
              <button class="pu-cal-nav-btn" @click="mesAnterior">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
              </button>
              <span class="pu-cal-titulo">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
              <button class="pu-cal-nav-btn" @click="mesSiguiente">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </button>
            </div>

            <div class="pu-cal-grid">
              <div class="pu-cal-nombre-dia">LU</div>
              <div class="pu-cal-nombre-dia">MA</div>
              <div class="pu-cal-nombre-dia">MI</div>
              <div class="pu-cal-nombre-dia">JU</div>
              <div class="pu-cal-nombre-dia">VI</div>
              <div class="pu-cal-nombre-dia">SA</div>
              <div class="pu-cal-nombre-dia">DO</div>

              <div v-for="(celda, i) in celdas" :key="i" class="pu-cal-dia" :class="{ 'pu-cal-hoy': celda.hoy, 'pu-cal-otro-mes': celda.otroMes }">
                {{ celda.dia }}
                <span v-if="celda.conTurno" class="pu-cal-punto"></span>
              </div>
            </div>

            <div class="pu-cal-leyenda">
              <span class="pu-cal-punto-leyenda"></span>Días con turnos
            </div>

            <button class="pu-cal-ver-completo" @click="emit('ir-a-calendario-usuario')">
              <svg style="width: 1.125rem; height: 1.125rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="5" width="18" height="16" rx="2" />
                <path d="M16 3v4M8 3v4M3 10h18" />
              </svg>
              Ver calendario completo
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pu-contenido {
  background-color: #eaf2fb;
  min-height: 100vh;
  padding-top: 4.9rem;
}

.pu-encabezado {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 2.5rem 2.5rem 1.5rem;
}

.pu-titulo-bienvenida {
  font-family: 'Inter', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.pu-subtitulo-bienvenida {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.pu-boton-reservar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #3d6fc2;
  color: #ffffff;
  border: none;
  border-radius: 1rem;
  padding: 0.75rem 1.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.pu-boton-reservar:hover {
  opacity: 0.9;
}

.pu-main-layout {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 2rem;
  padding: 0 2.5rem 2.5rem;
}

.pu-tarjeta {
  background-color: #ffffff;
  border-radius: 1.25rem;
  box-shadow: 0 0.25rem 1rem 0 rgba(15, 42, 86, 0.06);
  padding: 1.5rem;
}

.pu-tarjeta-turnos {
  display: flex;
  flex-direction: column;
}

.pu-tarjeta-turnos-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-bottom: 1.5rem;
}

.pu-tarjeta-titulo {
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.pu-badge-contador {
  background-color: #dcebfb;
  color: #3d6fc2;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.125rem 0.625rem;
  border-radius: 999px;
}

.pu-estado-turnos {
  color: #9ca3af;
  font-family: 'Inter', sans-serif;
  height: 10.75rem;
  padding-top: 0.5rem;
}

.pu-error {
  color: #dc2626;
}

.pu-lista-turnos {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: 10.75rem;
  overflow-y: auto;
  padding-right: 0.25rem;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.pu-lista-turnos::-webkit-scrollbar {
  width: 6px;
}

.pu-lista-turnos::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 999px;
}

.pu-fila-turno {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.pu-fila-turno:hover {
  background-color: #f8fafc;
}

.pu-fila-turno:hover .pu-chevron {
  color: #0ea5e9;
}

.pu-fecha-badge {
  width: 3.5rem;
  height: 3.5rem;
  flex-shrink: 0;
  border-radius: 1rem;
  background-color: #eaf2fb;
  color: #3d6fc2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pu-fecha-dia {
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1;
}

.pu-fecha-mes {
  font-family: 'Inter', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-top: 0.125rem;
}

.pu-fila-turno-info {
  flex: 1;
  min-width: 0;
  display: grid;
  grid-template-columns: 1fr 1.4fr 6rem;
  gap: 1.5rem;
  align-items: center;
  font-family: 'Inter', sans-serif;
}

.pu-fila-turno-columna {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.pu-fila-turno-etiqueta {
  font-size: 0.85rem;
  font-weight: 500;
  color: #9ca3af;
}

.pu-fila-turno-valor {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pu-fila-turno-reloj {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #64748b;
}

.pu-chevron {
  flex-shrink: 0;
  color: #94a3b8;
  transition: color 0.2s ease;
}

.pu-tarjeta-turnos-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 0.0625rem solid #f1f5f9;
  font-size: 0.85rem;
  color: #6b7280;
}

.pu-enlace {
  color: #3d6fc2;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}

.pu-enlace:hover {
  text-decoration: underline;
}

.pu-fila-tarjetas-chicas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.pu-tarjeta-chica-titulo {
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.pu-tarjeta-chica-desc {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.pu-cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.pu-cal-nav-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  border: 0.0625rem solid #e2e8f0;
  background-color: #ffffff;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.pu-cal-nav-btn:hover {
  background-color: #f8fafc;
}

.pu-cal-titulo {
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
}

.pu-cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  text-align: center;
}

.pu-cal-nombre-dia {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  padding-bottom: 0.5rem;
}

.pu-cal-dia {
  position: relative;
  padding: 0.5rem 0;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: #334155;
  border-radius: 0.75rem;
}

.pu-cal-otro-mes {
  color: #cbd5e1;
}

.pu-cal-hoy {
  background-color: #3d6fc2;
  color: #ffffff;
  font-weight: 700;
}

.pu-cal-punto {
  position: absolute;
  bottom: 0.1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 0.25rem;
  height: 0.25rem;
  border-radius: 999px;
  background-color: #3d6fc2;
}

.pu-cal-hoy .pu-cal-punto {
  background-color: #ffffff;
}

.pu-cal-leyenda {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: #64748b;
}

.pu-cal-punto-leyenda {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background-color: #3d6fc2;
  display: inline-block;
}

.pu-cal-ver-completo {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding: 0.75rem;
  background-color: #3d6fc2;
  color: #ffffff;
  border: none;
  border-radius: 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
  margin-top: 5.8rem;
}

.pu-cal-ver-completo:hover {
  opacity: 0.9;
}
</style>
