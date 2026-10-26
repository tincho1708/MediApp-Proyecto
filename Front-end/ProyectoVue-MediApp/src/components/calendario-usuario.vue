<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const props = defineProps<{ fechaInicial?: string | null }>()
const emit = defineEmits([
  'ir-a-profesionales',
  'ir-a-bienvenida',
  'ir-a-principal-usuario',
  'ir-a-chatbot',
  'ir-a-reservar-turno',
  'ir-a-calendario-usuario',
  'ir-a-mi-usuario-paciente',
  'ir-a-notificaciones',
])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const hoy = new Date()
// Si se llega desde un turno puntual, el calendario abre en ese día
const fechaInicial = props.fechaInicial ? new Date(props.fechaInicial) : hoy
const mesActual = ref(fechaInicial.getMonth())
const añoActual = ref(fechaInicial.getFullYear())

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

const nombresDia = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

const seleccionado = ref(
  new Date(fechaInicial.getFullYear(), fechaInicial.getMonth(), fechaInicial.getDate()),
)

const diasConTurno = computed(() => {
  const set = new Set<number>()
  for (const t of turnos.value) {
    if (t.estado?.estado !== 'aceptado') continue
    const f = new Date(t.fecha_hora)
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
      seleccionado:
        d === seleccionado.value.getDate() &&
        mesActual.value === seleccionado.value.getMonth() &&
        añoActual.value === seleccionado.value.getFullYear(),
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

function seleccionarDia(celda: { dia?: number; otroMes?: boolean }) {
  if (celda.otroMes || !celda.dia) return
  seleccionado.value = new Date(añoActual.value, mesActual.value, celda.dia)
}

function irAHoy() {
  seleccionado.value = new Date()
  mesActual.value = hoy.getMonth()
  añoActual.value = hoy.getFullYear()
}

function correrDias(n: number) {
  return new Date(
    seleccionado.value.getFullYear(),
    seleccionado.value.getMonth(),
    seleccionado.value.getDate() + n,
  )
}

const anterior = computed(() => correrDias(-1))
const siguiente = computed(() => correrDias(1))

function diaAnterior() {
  seleccionado.value = correrDias(-1)
}

function diaSiguiente() {
  seleccionado.value = correrDias(1)
}

type Turno = {
  id_turno: number
  fecha_hora: string
  notas: string | null
  estado: { estado: string }
  medico: {
    nombre: string
    apellido: string
    especialidades: { nombre_especialidad: string }[]
  }
}

const turnoSeleccionado = ref<Turno | null>(null)

function abrirTurno(t: Turno) {
  turnoSeleccionado.value = t
}
function cerrarTurno() {
  turnoSeleccionado.value = null
}
function inicialesMedico(t: Turno) {
  return `${t.medico.nombre[0] ?? ''}${t.medico.apellido[0] ?? ''}`.toUpperCase()
}

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'
const turnos = ref<Turno[]>([])

async function cargarTurnos() {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) return
    turnos.value = await res.json()
  } catch {}
}

onMounted(cargarTurnos)

let intervaloTurnos: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  intervaloTurnos = setInterval(cargarTurnos, 6000)
})
onBeforeUnmount(() => {
  if (intervaloTurnos !== undefined) clearInterval(intervaloTurnos)
})

function esMismoDia(fechaHora: string, dia: Date) {
  const f = new Date(fechaHora)
  return (
    f.getFullYear() === dia.getFullYear() &&
    f.getMonth() === dia.getMonth() &&
    f.getDate() === dia.getDate()
  )
}

const turnosDelDia = computed(() => {
  return turnos.value
    .filter((t) => t.estado?.estado === 'aceptado' && esMismoDia(t.fecha_hora, seleccionado.value))
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
})

function formatearHoraTurno(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}
function especialidadTurno(t: Turno) {
  return t.medico.especialidades[0]?.nombre_especialidad ?? 'Consulta'
}
function nombreMedicoTurno(t: Turno) {
  return `Dr. ${t.medico.nombre} ${t.medico.apellido}`
}

function fechaCorta(d: Date) {
  return `${nombresDia[d.getDay()]} ${d.getDate()} de ${nombresMes[d.getMonth()].toLowerCase()}`
}
function fechaLarga(d: Date) {
  return `${fechaCorta(d)} de ${d.getFullYear()}`
}
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

    <div class="h-screen overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
      <div class="flex items-start justify-between max-w-328 w-full mx-auto px-16 pt-10 pb-6 shrink-0">
        <div>
          <div class="text-3xl font-semibold text-slate-900">Mi calendario</div>
          <p class="text-sm text-slate-500 mt-1.5">
            Consultá tus turnos y accedé a la información de cada consulta.
          </p>
        </div>
        <button class="flex items-center gap-2 bg-[#3D6FC2] hover:opacity-90 transition-opacity text-white rounded-xl px-5 py-3 text-sm font-medium cursor-pointer" @click="emit('ir-a-reservar-turno')">
          <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Reservar turno
        </button>
      </div>

      <div class="flex-1 min-h-0 grid grid-cols-[20rem_1fr] gap-6 max-w-328 w-full mx-auto px-16 pb-10">
        <div class="bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-5 flex flex-col gap-3 min-h-0 overflow-hidden">
          <div class="flex items-center justify-between shrink-0">
            <span class="text-lg font-semibold text-slate-900"
              >{{ nombresMes[mesActual] }} {{ añoActual }}</span
            >
            <div class="flex gap-2">
              <button class="w-9 h-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="mesAnterior">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
              </button>
              <button class="w-9 h-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="mesSiguiente">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </button>
            </div>
          </div>

          <div class="flex-1 min-h-0 flex flex-col gap-1">
            <div class="grid grid-cols-7 shrink-0">
              <div class="text-center text-xs text-slate-400 pb-1">LU</div>
              <div class="text-center text-xs text-slate-400 pb-1">MA</div>
              <div class="text-center text-xs text-slate-400 pb-1">MI</div>
              <div class="text-center text-xs text-slate-400 pb-1">JU</div>
              <div class="text-center text-xs text-slate-400 pb-1">VI</div>
              <div class="text-center text-xs text-slate-400 pb-1">SA</div>
              <div class="text-center text-xs text-slate-400 pb-1">DO</div>
            </div>

            <div class="flex-1 min-h-0 grid grid-cols-7 grid-rows-6 gap-0.5">
              <div v-for="(celda, i) in celdas" :key="i" class="relative rounded-xl flex flex-col items-center justify-center gap-0.75 text-sm font-medium cursor-pointer transition-colors" :class=" celda.seleccionado ? 'bg-[#3D6FC2] text-white' : celda.otroMes ? 'text-slate-400 cursor-default' : 'text-slate-900 hover:bg-slate-100' " @click="seleccionarDia(celda)">
                <span>{{ celda.dia }}</span>
                <span v-if="celda.conTurno" class="w-0.75 h-0.75 rounded-full" :class="celda.seleccionado ? 'bg-white' : 'bg-[#3D6FC2]'"></span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 text-xs text-slate-400 shrink-0">
            <span class="w-1.5 h-1.5 rounded-full bg-[#3D6FC2] inline-block"></span>Día con turnos
          </div>

          <div class="h-px bg-slate-200 shrink-0"></div>

          <div class="bg-blue-50 rounded-2xl p-3 flex flex-col gap-1 shrink-0">
            <div class="text-sm font-medium text-[#3D6FC2]">{{ fechaCorta(seleccionado) }}</div>
            <div class="text-lg font-semibold text-slate-900">
              {{
                turnosDelDia.length
                  ? `${turnosDelDia.length} turno${turnosDelDia.length > 1 ? 's' : ''} programado${turnosDelDia.length > 1 ? 's' : ''}`
                  : 'Sin turnos programados'
              }}
            </div>
            <div v-if="turnosDelDia.length" class="text-xs text-slate-400">
              Primer turno a las {{ formatearHoraTurno(turnosDelDia[0].fecha_hora) }}
            </div>
          </div>

          <button class="w-full shrink-0 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl py-2.5 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="irAHoy">
            Ir a hoy
          </button>
        </div>

        <div class="bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-6 flex flex-col gap-6 min-h-0">
          <div class="flex items-start justify-between shrink-0">
            <div>
              <div class="text-lg font-semibold text-slate-900">Agenda del día</div>
              <p class="text-sm text-slate-500 mt-0.5">{{ fechaLarga(seleccionado) }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button class="w-9 h-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="diaAnterior">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
              </button>
              <button class="h-11 px-4 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="irAHoy">
                Hoy
              </button>
              <button class="w-9 h-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="diaSiguiente">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 shrink-0">
            <div class="flex items-center gap-3 p-4 rounded-2xl bg-slate-50">
              <span class="text-3xl font-semibold text-slate-400">{{ anterior.getDate() }}</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium text-slate-400">{{
                  nombresDia[anterior.getDay()]
                }}</span>
                <span class="text-xs text-slate-400"
                  >{{ nombresMes[anterior.getMonth()] }} de {{ anterior.getFullYear() }}</span
                >
              </div>
            </div>
            <div class="flex items-center gap-3 p-4 rounded-2xl bg-blue-50 outline-1 -outline-offset-1 outline-[#3D6FC2]">
              <span class="text-3xl font-semibold text-[#3D6FC2]">{{
                seleccionado.getDate()
              }}</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium text-[#3D6FC2]">{{
                  nombresDia[seleccionado.getDay()]
                }}</span>
                <span class="text-xs text-slate-400"
                  >{{ nombresMes[seleccionado.getMonth()] }} de
                  {{ seleccionado.getFullYear() }}</span
                >
              </div>
            </div>
            <div class="flex items-center gap-3 p-4 rounded-2xl bg-slate-50">
              <span class="text-3xl font-semibold text-slate-400">{{ siguiente.getDate() }}</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium text-slate-400">{{
                  nombresDia[siguiente.getDay()]
                }}</span>
                <span class="text-xs text-slate-400"
                  >{{ nombresMes[siguiente.getMonth()] }} de {{ siguiente.getFullYear() }}</span
                >
              </div>
            </div>
          </div>

          <div class="flex-1 min-h-0 flex flex-col gap-3 overflow-hidden">
            <div class="flex items-center justify-between shrink-0">
              <span class="text-sm font-medium text-slate-900">Turnos programados</span>
              <span class="text-xs text-slate-400"
                >{{ turnosDelDia.length }} turno{{ turnosDelDia.length !== 1 ? 's' : '' }}</span
              >
            </div>

            <div v-if="turnosDelDia.length" class="flex-1 min-h-0 flex flex-col gap-2 overflow-hidden">
              <div v-for="t in turnosDelDia" :key="t.id_turno" class="flex-1 min-h-0 flex items-center gap-4 px-5 bg-blue-50 outline-1 -outline-offset-1 outline-slate-200 rounded-2xl">
                <div class="flex flex-col shrink-0">
                  <span class="text-xl font-semibold text-[#3D6FC2]">{{
                    formatearHoraTurno(t.fecha_hora)
                  }}</span>
                  <span class="text-xs text-slate-400">Horario</span>
                </div>
                <div class="w-px self-stretch bg-slate-200"></div>
                <div class="flex-1 min-w-0 flex flex-col gap-0.5">
                  <span class="text-base font-semibold text-slate-900 truncate">{{
                    nombreMedicoTurno(t)
                  }}</span>
                  <span class="text-sm text-slate-500 truncate">{{ especialidadTurno(t) }}</span>
                </div>
                <button class="flex items-center gap-2 shrink-0 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl px-3 py-2 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="abrirTurno(t)">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 20h9M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4Z" />
                  </svg>
                  Ver turno
                </button>
              </div>
            </div>

            <div v-else class="flex-1 min-h-0 flex items-center gap-2 bg-slate-50 rounded-xl p-4 text-sm text-slate-500">
              <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6 9 17l-5-5" />
              </svg>
              No hay turnos programados para este día.
            </div>

            <div v-if="turnosDelDia.length" class="flex items-center gap-2 bg-slate-50 rounded-xl px-4 py-2.5 text-sm text-slate-500 shrink-0">
              <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6 9 17l-5-5" />
              </svg>
              No hay más turnos programados para este día.
            </div>
          </div>

          <p class="flex items-center gap-2 mt-auto text-xs text-slate-400 shrink-0">
            <svg style="width: 0.875rem; height: 0.875rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
            Abrí "Ver turno" para consultar sus detalles.
          </p>
        </div>
      </div>
    </div>

    <div v-if="turnoSeleccionado" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-6" @click="cerrarTurno">
      <div class="bg-white rounded-3xl p-8 w-lg max-w-full max-h-full overflow-hidden flex flex-col gap-5 font-['Inter']" @click.stop>
        <div class="flex items-start justify-between shrink-0">
          <span class="text-xl font-bold text-slate-900"
            >Tu consulta de {{ especialidadTurno(turnoSeleccionado) }}</span
          >
          <span class="text-sm text-slate-400 whitespace-nowrap">{{
            fechaCorta(new Date(turnoSeleccionado.fecha_hora))
          }}</span>
        </div>

        <div class="flex items-center gap-4 p-4 bg-slate-50 rounded-2xl shrink-0">
          <div class="w-12 h-12 shrink-0 rounded-full bg-blue-100 text-[#3D6FC2] font-semibold flex items-center justify-center">
            {{ inicialesMedico(turnoSeleccionado) }}
          </div>
          <div class="min-w-0">
            <div class="font-semibold text-slate-900 truncate">
              {{ nombreMedicoTurno(turnoSeleccionado) }}
            </div>
            <div class="text-sm text-slate-500 truncate">
              {{ especialidadTurno(turnoSeleccionado) }}
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between p-4 bg-blue-50 rounded-2xl shrink-0">
          <div class="flex items-center gap-3">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="5" width="18" height="16" rx="2" />
              <path d="M16 3v4M8 3v4M3 10h18" />
            </svg>
            <div>
              <div class="text-xs text-slate-400">Fecha del turno</div>
              <div class="font-semibold text-slate-900">
                {{ new Date(turnoSeleccionado.fecha_hora).getDate() }} de
                {{ nombresMes[new Date(turnoSeleccionado.fecha_hora).getMonth()].toLowerCase() }} de
                {{ new Date(turnoSeleccionado.fecha_hora).getFullYear() }}
              </div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-xs text-slate-400">Horario</div>
            <div class="text-xl font-semibold text-[#3D6FC2]">
              {{ formatearHoraTurno(turnoSeleccionado.fecha_hora) }}
            </div>
          </div>
        </div>

        <div class="flex-1 min-h-0 flex flex-col gap-2 overflow-hidden">
          <span class="text-sm font-semibold text-slate-900 shrink-0">Notas</span>
          <div class="flex-1 min-h-0 overflow-hidden bg-slate-50 rounded-xl p-4 text-sm text-slate-500">
            {{ turnoSeleccionado.notas || 'No hay notas agregadas para este turno.' }}
          </div>
        </div>

        <button class="shrink-0 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl px-5 py-2.5 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors self-start" @click="cerrarTurno">
          Volver al calendario
        </button>
      </div>
    </div>
  </div>
</template>
