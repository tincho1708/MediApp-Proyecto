<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

// Si se llega desde "Solicitar turno" en Profesionales, viene el médico ya elegido
const props = defineProps<{ medicoInicialId?: number | null }>()
const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal-usuario',
  'ir-a-chatbot',
  'ir-a-calendario-usuario',
  'ir-a-mi-usuario-paciente',
  'ir-a-notificaciones',
  'ir-a-profesionales',
])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()
const esta = ref(false)
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Especialidad = {
  id_especialidad: number
  nombre_especialidad: string
}

type Medico = {
  id: number
  nombre: string
  apellido: string
  telefono: string | null
  mail: string
  especialidades: Especialidad[]
}

const medicos = ref<Medico[]>([])
const cargandoMedicos = ref(true)
const errorMedicos = ref('')

const especialidadSeleccionada = ref<number | null>(null)
const medicoSeleccionado = ref<Medico | null>(null)

async function cargarMedicos() {
  cargandoMedicos.value = true
  errorMedicos.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos`)
    if (!res.ok) throw new Error()
    medicos.value = await res.json()
    const medicoInicial = medicos.value.find((m) => m.id === props.medicoInicialId)
    if (medicoInicial) {
      medicoSeleccionado.value = medicoInicial
      continuarAPaso2()
    }
  } catch {
    errorMedicos.value = 'No se pudieron cargar los profesionales. Intentá de nuevo más tarde.'
  } finally {
    cargandoMedicos.value = false
  }
}

onMounted(cargarMedicos)

const especialidadesDisponibles = computed<Especialidad[]>(() => {
  const vistas = new Map<number, Especialidad>()
  for (const m of medicos.value) {
    for (const esp of m.especialidades) {
      if (!vistas.has(esp.id_especialidad)) vistas.set(esp.id_especialidad, esp)
    }
  }
  return [...vistas.values()].sort((a, b) =>
    a.nombre_especialidad.localeCompare(b.nombre_especialidad),
  )
})

const medicosFiltrados = computed(() => {
  if (especialidadSeleccionada.value === null) return medicos.value
  return medicos.value.filter((m) =>
    m.especialidades.some((e) => e.id_especialidad === especialidadSeleccionada.value),
  )
})

function elegirEspecialidad(id: number) {
  especialidadSeleccionada.value = especialidadSeleccionada.value === id ? null : id
  if (
    medicoSeleccionado.value &&
    !medicoSeleccionado.value.especialidades.some(
      (e) => e.id_especialidad === especialidadSeleccionada.value,
    )
  ) {
    medicoSeleccionado.value = null
  }
}

function elegirMedico(m: Medico) {
  medicoSeleccionado.value = medicoSeleccionado.value?.id === m.id ? null : m
}

function iniciales(m: Medico) {
  return `${m.nombre.charAt(0)}${m.apellido.charAt(0)}`.toUpperCase()
}
function especialidadesTexto(m: Medico) {
  return m.especialidades.length
    ? m.especialidades.map((e) => e.nombre_especialidad).join(', ')
    : 'Sin especialidad'
}

const pasoActual = ref(1)

const nombresPaso = ['Profesional', 'Fecha y hora', 'Revisar datos']

// Una vez confirmada la reserva, todos los pasos quedan completos
function pasoCompletado(n: number) {
  return turnoConfirmado.value || pasoActual.value > n
}

function claseCirculoPaso(n: number) {
  if (pasoCompletado(n))
    return 'bg-blue-50 outline-1 -outline-offset-1 outline-blue-200 text-sky-700'
  if (pasoActual.value === n) return 'bg-sky-700 text-white'
  return 'bg-slate-100 text-slate-400'
}
function claseTextoPaso(n: number) {
  return pasoActual.value >= n ? 'text-sky-700' : 'text-slate-400'
}

function continuarAPaso2() {
  if (!medicoSeleccionado.value) return
  pasoActual.value = 2
  cargarHorarios(medicoSeleccionado.value.id)
}
function volverAPaso1() {
  pasoActual.value = 1
}

function continuarAPaso3() {
  if (!diaSeleccionado.value || !horaSeleccionada.value) return
  pasoActual.value = 3
}
function volverAPaso2() {
  pasoActual.value = 2
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
const nombresDia = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

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

const celdas = computed(() => {
  const ultimoDia = new Date(añoActual.value, mesActual.value + 1, 0).getDate()
  const primerDia = new Date(añoActual.value, mesActual.value, 1).getDay()
  const offset = (primerDia + 6) % 7
  const ultimoDiaMesAnterior = new Date(añoActual.value, mesActual.value, 0).getDate()
  const resultado = []

  for (let i = offset; i > 0; i--) {
    resultado.push({ dia: ultimoDiaMesAnterior - i + 1, otroMes: true })
  }

  const inicioHoy = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate())

  for (let d = 1; d <= ultimoDia; d++) {
    resultado.push({
      dia: d,
      hoy:
        d === hoy.getDate() &&
        mesActual.value === hoy.getMonth() &&
        añoActual.value === hoy.getFullYear(),
      pasado: new Date(añoActual.value, mesActual.value, d) < inicioHoy,
    })
  }

  let siguiente = 1
  while (resultado.length % 7 !== 0) {
    resultado.push({ dia: siguiente, otroMes: true })
    siguiente++
  }

  return resultado
})

const diaSeleccionado = ref<number | null>(null)

function elegirDia(celda: { dia?: number; otroMes?: boolean; pasado?: boolean }) {
  if (celda.otroMes || celda.pasado || celda.dia === undefined) return
  diaSeleccionado.value = celda.dia
  horaSeleccionada.value = null
  if (medicoSeleccionado.value) cargarHorasOcupadas(medicoSeleccionado.value.id, celda.dia)
}

type Horario = {
  id: number
  dia_semana: number
  hora: number
}

const horarios = ref<Horario[]>([])
const cargandoHorarios = ref(false)
const errorHorarios = ref('')
const horaSeleccionada = ref<number | null>(null)
const horasOcupadas = ref<number[]>([])

async function cargarHorarios(medicoId: number) {
  cargandoHorarios.value = true
  errorHorarios.value = ''
  horarios.value = []
  horaSeleccionada.value = null
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos/${medicoId}/horarios`)
    if (!res.ok) throw new Error()
    horarios.value = await res.json()
  } catch {
    errorHorarios.value = 'No se pudieron cargar los horarios. Intentá de nuevo más tarde.'
  } finally {
    cargandoHorarios.value = false
  }
}

async function cargarHorasOcupadas(medicoId: number, dia: number, silencioso = false) {
  if (!silencioso) horasOcupadas.value = []
  try {
    const pad = (n: number) => String(n).padStart(2, '0')
    const fecha = `${añoActual.value}-${pad(mesActual.value + 1)}-${pad(dia)}`
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/medicos/${medicoId}/horarios-ocupados?fecha=${fecha}`,
    )
    if (!res.ok) throw new Error()
    horasOcupadas.value = await res.json()
  } catch {}
}

let intervaloOcupadas: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  intervaloOcupadas = setInterval(() => {
    if (medicoSeleccionado.value && diaSeleccionado.value !== null) {
      cargarHorasOcupadas(medicoSeleccionado.value.id, diaSeleccionado.value, true)
    }
  }, 6000)
})
onBeforeUnmount(() => {
  if (intervaloOcupadas !== undefined) clearInterval(intervaloOcupadas)
})

const diaSemanaSeleccionado = computed(() => {
  if (diaSeleccionado.value === null) return null
  const fecha = new Date(añoActual.value, mesActual.value, diaSeleccionado.value)
  return (fecha.getDay() + 6) % 7
})

const esHoySeleccionado = computed(() => {
  return (
    diaSeleccionado.value === hoy.getDate() &&
    mesActual.value === hoy.getMonth() &&
    añoActual.value === hoy.getFullYear()
  )
})

const horariosDelDia = computed(() => {
  if (diaSemanaSeleccionado.value === null) return []
  let lista = horarios.value.filter((h) => h.dia_semana === diaSemanaSeleccionado.value)
  lista = lista.filter((h) => !horasOcupadas.value.includes(h.hora))
  if (esHoySeleccionado.value) {
    lista = lista.filter((h) => h.hora > hoy.getHours())
  }
  return lista.sort((a, b) => a.hora - b.hora)
})

function formatearHora(hora: number) {
  return `${String(hora).padStart(2, '0')}:00`
}
function horaTexto(h: Horario) {
  return formatearHora(h.hora)
}

const resumenFechaHora = computed(() => {
  if (diaSeleccionado.value === null || horaSeleccionada.value === null) return ''
  return `${diaSeleccionado.value} de ${nombresMes[mesActual.value].toLowerCase()} - ${formatearHora(horaSeleccionada.value)}`
})

const fechaSeleccionadaTexto = computed(() => {
  if (diaSeleccionado.value === null) return ''
  const fecha = new Date(añoActual.value, mesActual.value, diaSeleccionado.value)
  return `${nombresDia[fecha.getDay()]} ${diaSeleccionado.value} de ${nombresMes[mesActual.value].toLowerCase()}`
})

const fechaHoraElegidaTexto = computed(() => {
  if (diaSeleccionado.value === null || horaSeleccionada.value === null) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(diaSeleccionado.value)}/${pad(mesActual.value + 1)}/${añoActual.value} · ${formatearHora(horaSeleccionada.value)}`
})

const fechaSeleccionadaTextoConAño = computed(() => {
  if (!fechaSeleccionadaTexto.value) return ''
  return `${fechaSeleccionadaTexto.value} de ${añoActual.value}`
})

function elegirHora(h: Horario) {
  horaSeleccionada.value = horaSeleccionada.value === h.hora ? null : h.hora
}

const fechaHoraISO = computed(() => {
  if (diaSeleccionado.value === null || horaSeleccionada.value === null) return null
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${añoActual.value}-${pad(mesActual.value + 1)}-${pad(diaSeleccionado.value)}T${pad(horaSeleccionada.value)}:00:00`
})

const reservando = ref(false)
const errorReserva = ref('')
const turnoConfirmado = ref(false)
const motivoConsulta = ref('')

async function confirmarReserva() {
  if (!medicoSeleccionado.value || !fechaHoraISO.value) return
  reservando.value = true
  errorReserva.value = ''
  try {
    const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${sesion.token}`,
      },
      body: JSON.stringify({
        medico_id: medicoSeleccionado.value.id,
        fecha_hora: fechaHoraISO.value,
        notas: motivoConsulta.value || null,
      }),
    })
    const data = await res.json()
    if (!res.ok) {
      errorReserva.value = data.detail || 'No se pudo reservar el turno.'
      return
    }
    turnoConfirmado.value = true
  } catch {
    errorReserva.value = 'No se pudo conectar al servidor.'
  } finally {
    reservando.value = false
  }
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
        <button class="campoo activo">Reservar turno<span class="campoo-indicador"></span></button>
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

    <div class="h-screen overflow-hidden bg-linear-to-br from-blue-100 via-violet-100 to-blue-200 pt-[4.9rem] flex flex-col font-['Inter']">
      <!-- Contenedor común: título, pasos y tarjeta comparten el mismo ancho y borde izquierdo -->
      <div class="flex-1 min-h-0 flex flex-col max-w-328 w-full mx-auto px-4 sm:px-8">
        <div class="flex items-start justify-between gap-4 pt-10 pb-6 shrink-0">
          <div v-if="turnoConfirmado">
            <div class="text-3xl font-semibold text-slate-900">Turno reservado</div>
            <p class="text-sm text-slate-500 mt-1.5">
              La reserva se completó. Podés consultar los detalles en tus turnos.
            </p>
          </div>
          <div v-else>
            <div class="text-3xl font-semibold text-slate-900">Reservar turno</div>
            <p class="text-sm text-slate-500 mt-1.5">
              Elegí la especialidad y el profesional con quien querés atenderte.
            </p>
          </div>
          <span class="text-sm font-medium text-sky-700 whitespace-nowrap"
            >Paso {{ pasoActual }} de {{ nombresPaso.length }}</span
          >
        </div>

        <div class="flex items-center pb-6 shrink-0">
          <template v-for="(nombre, idx) in nombresPaso" :key="idx">
            <div class="flex items-center gap-3">
              <div class="size-9 shrink-0 rounded-xl flex items-center justify-center text-sm font-medium transition-colors" :class="claseCirculoPaso(idx + 1)">
                <svg v-if="pasoCompletado(idx + 1)" style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6 9 17l-5-5" />
                </svg>
                <template v-else>{{ idx + 1 }}</template>
              </div>
              <span class="text-sm font-medium whitespace-nowrap transition-colors" :class="claseTextoPaso(idx + 1)">{{ nombre }}</span
              >
            </div>
            <div v-if="idx < nombresPaso.length - 1" class="flex-1 h-0.5 bg-slate-200 mx-4 min-w-8"></div>
          </template>
        </div>

        <div class="bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-6 w-full mb-8 flex-1 min-h-0 flex flex-col gap-6">
          <Transition name="fade" mode="out-in">
            <div v-if="pasoActual === 1" key="paso1" class="flex-1 min-h-0 flex flex-col gap-4">
              <div class="flex-1 min-h-0 grid grid-cols-[1fr_22rem] gap-6">
                <div class="min-h-0 flex flex-col gap-6">
                  <span class="text-lg font-semibold text-slate-900 shrink-0"
                    >1. Seleccioná un profesional</span
                  >

                  <div v-if="especialidadesDisponibles.length" class="flex flex-col gap-3 shrink-0">
                    <span class="text-sm font-medium text-slate-900">Especialidad</span>
                    <div class="flex flex-wrap gap-3">
                      <button v-for="esp in especialidadesDisponibles" :key="esp.id_especialidad" @click="elegirEspecialidad(esp.id_especialidad)" class="h-11 px-4 rounded-xl text-sm font-medium cursor-pointer transition-colors" :class=" especialidadSeleccionada === esp.id_especialidad ? 'bg-sky-700 text-white' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 hover:bg-slate-50' ">
                        {{ esp.nombre_especialidad }}
                      </button>
                    </div>
                  </div>

                  <p v-if="cargandoMedicos" class="text-slate-400 text-sm">
                    Cargando profesionales...
                  </p>
                  <p v-else-if="errorMedicos" class="text-red-500 text-sm">{{ errorMedicos }}</p>
                  <p v-else-if="!medicosFiltrados.length" class="text-slate-400 text-sm">
                    No hay profesionales disponibles para esta especialidad.
                  </p>

                  <div v-else class="flex-1 min-h-0 flex flex-col gap-3 overflow-y-auto">
                    <button v-for="m in medicosFiltrados" :key="m.id" @click="elegirMedico(m)" class="shrink-0 flex items-center gap-4 px-5 py-4 rounded-2xl text-left cursor-pointer transition-colors" :class=" medicoSeleccionado?.id === m.id ? 'bg-blue-50 outline-1 -outline-offset-1 outline-sky-700' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 hover:bg-slate-50' ">
                      <div class="size-12 shrink-0 rounded-full bg-blue-100 text-sky-700 flex items-center justify-center text-sm font-medium">
                        {{ iniciales(m) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="font-semibold text-slate-900 truncate">
                          {{ m.nombre }} {{ m.apellido }}
                        </div>
                        <div class="text-sm text-slate-500 truncate">
                          {{ especialidadesTexto(m) }}
                        </div>
                      </div>
                      <div class="size-6 shrink-0 rounded-xl flex items-center justify-center transition-colors" :class=" medicoSeleccionado?.id === m.id ? 'bg-sky-700' : 'bg-white outline-1 -outline-offset-1 outline-slate-200' ">
                        <svg v-if="medicoSeleccionado?.id === m.id" style="width: 0.875rem; height: 0.875rem" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M20 6 9 17l-5-5" />
                        </svg>
                      </div>
                    </button>
                  </div>
                </div>

                <div class="min-h-0 bg-slate-50 rounded-2xl p-6 flex flex-col gap-4 overflow-hidden">
                  <span class="text-lg font-semibold text-slate-900 shrink-0">Tu reserva</span>

                  <template v-if="medicoSeleccionado">
                    <div class="flex items-center gap-3 shrink-0">
                      <div class="size-11 shrink-0 rounded-full bg-blue-100 text-sky-700 flex items-center justify-center text-sm font-medium">
                        {{ iniciales(medicoSeleccionado) }}
                      </div>
                      <div class="min-w-0">
                        <div class="font-semibold text-slate-900 truncate">
                          {{ medicoSeleccionado.nombre }} {{ medicoSeleccionado.apellido }}
                        </div>
                        <div class="text-sm text-slate-500 truncate">
                          {{ especialidadesTexto(medicoSeleccionado) }}
                        </div>
                      </div>
                    </div>

                    <div class="h-px bg-slate-200 shrink-0"></div>

                    <div class="shrink-0">
                      <div class="text-xs font-medium text-slate-400 tracking-wide">
                        FECHA Y HORA
                      </div>
                      <div class="text-sm text-slate-500 mt-1">
                        {{ resumenFechaHora || 'A elegir en el siguiente paso' }}
                      </div>
                    </div>
                  </template>
                  <p v-else class="text-sm text-slate-400">
                    Seleccioná un profesional para continuar.
                  </p>
                </div>
              </div>

              <div class="flex items-center justify-between shrink-0">
                <button @click="emit('ir-a-principal-usuario')" class="flex items-center gap-2 h-11 px-4 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-sky-700 cursor-pointer hover:bg-slate-50 transition-colors">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  Volver
                </button>
                <button @click="continuarAPaso2" class="h-11 px-5 rounded-xl bg-sky-700 text-white text-sm font-medium cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed" :disabled="!medicoSeleccionado">
                  Continuar
                </button>
              </div>
            </div>

            <div v-else-if="pasoActual === 2" key="paso2" class="flex-1 min-h-0 flex flex-col gap-4">
              <div class="flex-1 min-h-0 grid grid-cols-[1fr_28rem] gap-6">
                <div class="min-h-0 flex flex-col gap-4">
                  <div class="flex items-center justify-between shrink-0">
                    <button @click="mesAnterior" class="size-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors">
                      <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M15 18l-6-6 6-6" />
                      </svg>
                    </button>
                    <span class="text-lg font-semibold text-slate-900"
                      >{{ nombresMes[mesActual] }} {{ añoActual }}</span
                    >
                    <button @click="mesSiguiente" class="size-9 shrink-0 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors">
                      <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9 18l6-6-6-6" />
                      </svg>
                    </button>
                  </div>

                  <div class="grid grid-cols-7 shrink-0">
                    <div class="text-center text-xs text-slate-400 pb-1">LU</div>
                    <div class="text-center text-xs text-slate-400 pb-1">MA</div>
                    <div class="text-center text-xs text-slate-400 pb-1">MI</div>
                    <div class="text-center text-xs text-slate-400 pb-1">JU</div>
                    <div class="text-center text-xs text-slate-400 pb-1">VI</div>
                    <div class="text-center text-xs text-slate-400 pb-1">SA</div>
                    <div class="text-center text-xs text-slate-400 pb-1">DO</div>
                  </div>

                  <div class="flex-1 min-h-0 grid grid-cols-7 grid-rows-6 gap-2">
                    <button v-for="(celda, i) in celdas" :key="i" @click="elegirDia(celda)" :disabled="celda.otroMes || celda.pasado" class="relative rounded-xl flex flex-col items-center justify-center gap-0.75 text-sm font-medium transition-colors" :class="[ celda.otroMes || celda.pasado ? 'text-slate-300 cursor-default' : 'text-slate-900 cursor-pointer hover:bg-slate-100', !celda.otroMes && celda.dia === diaSeleccionado ? 'bg-sky-700 text-white hover:bg-sky-700' : '', ]">
                      {{ celda.dia }}
                    </button>
                  </div>

                  <p v-if="diaSeleccionado" class="text-xs text-sky-700 shrink-0">
                    Fecha seleccionada: {{ fechaSeleccionadaTexto.toLowerCase() }}
                  </p>
                </div>

                <div class="min-h-0 bg-slate-50 rounded-2xl p-6 flex flex-col gap-4 overflow-hidden">
                  <span class="text-lg font-semibold text-slate-900 shrink-0"
                    >Horarios disponibles</span
                  >

                  <template v-if="diaSeleccionado">
                    <div class="shrink-0">
                      <div class="text-sm font-medium text-sky-700">
                        {{ fechaSeleccionadaTexto }}
                      </div>
                      <div v-if="medicoSeleccionado" class="text-sm text-slate-500 mt-1">
                        {{ medicoSeleccionado.nombre }} {{ medicoSeleccionado.apellido }} ·
                        {{ especialidadesTexto(medicoSeleccionado) }}
                      </div>
                    </div>

                    <p v-if="cargandoHorarios" class="text-sm text-slate-400 shrink-0">
                      Cargando horarios...
                    </p>
                    <p v-else-if="errorHorarios" class="text-sm text-red-600 shrink-0">
                      {{ errorHorarios }}
                    </p>
                    <p v-else-if="!horariosDelDia.length" class="text-sm text-slate-400 shrink-0">
                      No hay horarios disponibles para este día.
                    </p>

                    <div v-else class="flex gap-3 overflow-x-auto pb-1 shrink-0">
                      <button v-for="h in horariosDelDia" :key="h.id" @click="elegirHora(h)" class="shrink-0 w-24 h-11 rounded-xl text-sm font-medium cursor-pointer transition-colors" :class=" horaSeleccionada === h.hora ? 'bg-sky-700 text-white' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 hover:bg-slate-100' ">
                        {{ horaTexto(h) }}
                      </button>
                    </div>

                    <template v-if="horaSeleccionada">
                      <div class="h-px bg-slate-200 shrink-0"></div>
                      <div class="shrink-0">
                        <div class="text-xs font-medium text-slate-400 tracking-wide">
                          TU ELECCIÓN
                        </div>
                        <div class="text-lg font-semibold text-sky-700 mt-1">
                          {{ fechaHoraElegidaTexto }}
                        </div>
                        <p class="text-sm text-slate-500 mt-1">
                          Continuá para revisar los datos antes de confirmar.
                        </p>
                      </div>
                    </template>
                  </template>
                  <p v-else class="text-sm text-slate-400">
                    Elegí un día en el calendario para ver los horarios.
                  </p>
                </div>
              </div>

              <div class="flex items-center justify-between shrink-0">
                <button @click="volverAPaso1" class="flex items-center gap-2 h-11 px-4 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-sky-700 cursor-pointer hover:bg-slate-50 transition-colors">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  Volver
                </button>
                <button @click="continuarAPaso3" class="h-11 px-5 rounded-xl bg-sky-700 text-white text-sm font-medium cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed" :disabled="!diaSeleccionado || !horaSeleccionada">
                  Continuar
                </button>
              </div>
            </div>

            <div v-else key="paso3" class="flex-1 min-h-0 flex flex-col gap-6">
              <div v-if="turnoConfirmado" class="flex-1 min-h-0 overflow-y-auto">
                <div class="min-h-full flex flex-col items-center justify-center gap-6 text-center py-4">
                  <div class="size-16 shrink-0 bg-emerald-50 rounded-full flex items-center justify-center">
                    <svg style="width: 2.25rem; height: 2.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-teal-700">
                      <path d="M20 6 9 17l-5-5" />
                    </svg>
                  </div>

                  <div class="flex flex-col gap-2">
                    <p class="text-2xl sm:text-3xl font-semibold text-slate-900">
                      ¡Tu turno está reservado!
                    </p>
                    <p class="text-sm text-slate-500">
                      Le avisamos al profesional para que lo confirme. Cuando lo acepte, vas a verlo
                      en tu calendario.
                    </p>
                  </div>

                  <div v-if="medicoSeleccionado" class="w-full max-w-204 p-6 bg-slate-50 rounded-2xl flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8 text-left">
                    <div class="flex-1 min-w-0 flex flex-col gap-2">
                      <span class="text-lg font-semibold text-slate-900 truncate"
                        >Dr. {{ medicoSeleccionado.nombre }} {{ medicoSeleccionado.apellido }}</span
                      >
                      <span class="text-sm text-slate-500 truncate">{{
                        especialidadesTexto(medicoSeleccionado)
                      }}</span>
                      <span v-if="motivoConsulta" class="text-xs text-slate-500 line-clamp-2"
                        >Motivo: {{ motivoConsulta }}</span
                      >
                    </div>
                    <div class="h-px sm:h-20 sm:w-px bg-slate-200 shrink-0"></div>
                    <div class="flex-1 min-w-0 flex flex-col gap-2">
                      <span class="text-sm font-medium text-slate-900">{{
                        fechaSeleccionadaTextoConAño
                      }}</span>
                      <span class="text-lg font-semibold text-sky-700">{{
                        horaSeleccionada !== null ? formatearHora(horaSeleccionada) : ''
                      }}</span>
                      <span class="text-xs text-sky-700">Pendiente de confirmación</span>
                    </div>
                  </div>

                  <div class="w-full max-w-120 flex flex-col-reverse sm:flex-row gap-4">
                    <button @click="emit('ir-a-principal-usuario')" class="flex-1 h-11 px-5 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-sky-700 cursor-pointer hover:bg-slate-50 transition-colors">
                      Volver al inicio
                    </button>
                    <button @click="emit('ir-a-calendario-usuario', fechaHoraISO)" class="flex-1 h-11 px-5 rounded-xl bg-sky-700 text-white text-sm font-medium cursor-pointer hover:opacity-90 transition-opacity">
                      Ver mis turnos
                    </button>
                  </div>
                </div>
              </div>

              <template v-else>
                <div class="flex-1 min-h-0 grid grid-cols-[1fr_24rem] gap-6">
                  <div class="min-h-0 flex flex-col gap-4">
                    <div>
                      <span class="text-lg font-semibold text-slate-900"
                        >3. Revisá los datos del turno</span
                      >
                      <p class="text-sm text-slate-500 mt-1">
                        Comprobá el profesional, la fecha y el horario en el resumen.
                      </p>
                    </div>

                    <div class="flex-1 min-h-0 flex flex-col gap-2">
                      <span class="text-sm font-medium text-slate-900 shrink-0"
                        >Motivo de la consulta</span
                      >
                      <textarea v-model="motivoConsulta" placeholder="Contale al profesional el motivo de tu consulta…" class="flex-1 min-h-0 w-full bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-2xl p-4 text-sm text-slate-900 placeholder:text-slate-400 resize-none"></textarea>
                    </div>

                    <p v-if="errorReserva" class="text-sm text-red-600 shrink-0">
                      {{ errorReserva }}
                    </p>
                  </div>

                  <div class="min-h-0 bg-slate-50 rounded-2xl p-6 flex flex-col gap-4 overflow-hidden">
                    <span class="text-lg font-semibold text-slate-900 shrink-0">Tu reserva</span>

                    <template v-if="medicoSeleccionado">
                      <div class="flex items-center gap-3 shrink-0">
                        <div class="size-11 shrink-0 rounded-full bg-blue-100 text-sky-700 flex items-center justify-center text-sm font-medium">
                          {{ iniciales(medicoSeleccionado) }}
                        </div>
                        <div class="min-w-0">
                          <div class="font-semibold text-slate-900 truncate">
                            {{ medicoSeleccionado.nombre }} {{ medicoSeleccionado.apellido }}
                          </div>
                          <div class="text-sm text-slate-500 truncate">
                            {{ especialidadesTexto(medicoSeleccionado) }}
                          </div>
                        </div>
                      </div>

                      <div class="h-px bg-slate-200 shrink-0"></div>

                      <div class="shrink-0">
                        <div class="text-xs font-medium text-slate-400 tracking-wide">
                          FECHA Y HORA
                        </div>
                        <div class="text-sm font-medium text-slate-900 mt-1">
                          {{ fechaSeleccionadaTextoConAño }}
                        </div>
                        <div class="text-lg font-semibold text-sky-700 mt-1">
                          {{ horaSeleccionada !== null ? formatearHora(horaSeleccionada) : '' }}
                        </div>
                      </div>
                    </template>
                  </div>
                </div>

                <div class="flex items-center justify-between shrink-0">
                  <button @click="volverAPaso2" class="flex items-center gap-2 h-11 px-4 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-sky-700 cursor-pointer hover:bg-slate-50 transition-colors">
                    <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                    Volver
                  </button>
                  <button @click="confirmarReserva" class="h-11 px-5 rounded-xl bg-sky-700 text-white text-sm font-medium cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed" :disabled="!medicoSeleccionado || reservando">
                    {{ reservando ? 'Reservando...' : 'Confirmar turno' }}
                  </button>
                </div>
              </template>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>
