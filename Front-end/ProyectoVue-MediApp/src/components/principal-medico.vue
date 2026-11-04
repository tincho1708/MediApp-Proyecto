<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTurnosMedico, type TurnoMedico } from '@/stores/turnosMedico'
import { useMiStore } from '@/stores/useMiStore'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-mis-pacientes', 'ir-a-configuracion'])

const store = useMiStore()
const textoDeEntrada = ref()
const alHacerClick = (fechaHora: string) => {
  textoDeEntrada.value = fechaHora
  store.guardarVariable(textoDeEntrada.value)
  emit('ir-a-calendario')
}

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const nombresDia = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
const hoy = new Date()

function esMismoDia(fechaHora: string | Date, dia: Date) {
  const f = new Date(fechaHora)
  return f.getFullYear() === dia.getFullYear() && f.getMonth() === dia.getMonth() && f.getDate() === dia.getDate()
}

function formatearHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}

function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()}/${f.getMonth() + 1}`
}

function fechaCorta(d: Date) {
  return `${nombresDia[d.getDay()]} ${d.getDate()} de ${nombresMes[d.getMonth()].toLowerCase()}`
}

const { turnos, usarPollingTurnos } = useTurnosMedico()
usarPollingTurnos()

const coloresTurno = ['bg-indigo-500', 'bg-teal-600', 'bg-blue-400']

function nombrePaciente(t: TurnoMedico) {
  return `${t.paciente.nombre} ${t.paciente.apellido}`
}

function ordenarPorFecha(lista: TurnoMedico[]) {
  return [...lista].sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
}

function yaPaso(t: TurnoMedico) {
  return new Date(t.fecha_hora).getTime() < Date.now()
}

const turnosAceptados = computed(() => turnos.value.filter((t) => t.estado?.estado === 'aceptado'))
const turnosHoy = computed(() => ordenarPorFecha(turnosAceptados.value.filter((t) => esMismoDia(t.fecha_hora, hoy))))
const turnosHoyPendientes = computed(() => turnosHoy.value.filter((t) => !yaPaso(t)).length)
const progresoHoy = computed(() => (turnosHoy.value.length ? ((turnosHoy.value.length - turnosHoyPendientes.value) / turnosHoy.value.length) * 100 : 0))
const proximosTurnos = computed(() => ordenarPorFecha(turnosAceptados.value.filter((t) => !yaPaso(t))).slice(0, 3))
const proximoTurno = computed(() => proximosTurnos.value[0] ?? null)
const agenda = computed(() => (turnosHoy.value.length ? turnosHoy.value : proximosTurnos.value))

const mesActual = ref(hoy.getMonth())
const añoActual = ref(hoy.getFullYear())
const seleccionado = ref(hoy)

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
  const ultimoDiaMesAnterior = new Date(añoActual.value, mesActual.value, 0).getDate()
  const offset = (new Date(añoActual.value, mesActual.value, 1).getDay() + 6) % 7
  const resultado = []

  for (let i = offset; i > 0; i--) {
    resultado.push({ dia: ultimoDiaMesAnterior - i + 1, otroMes: true })
  }

  for (let d = 1; d <= ultimoDia; d++) {
    const fecha = new Date(añoActual.value, mesActual.value, d)
    resultado.push({
      dia: d,
      fecha,
      hoy: esMismoDia(fecha, hoy),
      seleccionado: esMismoDia(fecha, seleccionado.value),
      conTurno: turnosAceptados.value.some((t) => esMismoDia(t.fecha_hora, fecha)),
    })
  }

  let siguiente = 1
  while (resultado.length % 7 !== 0) {
    resultado.push({ dia: siguiente, otroMes: true })
    siguiente++
  }

  return resultado
})

function seleccionarDia(fecha?: Date) {
  if (fecha) seleccionado.value = fecha
}

const turnosSeleccionado = computed(() => turnosAceptados.value.filter((t) => esMismoDia(t.fecha_hora, seleccionado.value)).length)

const UNA_HORA = 60 * 60 * 1000
const CINCO_DIAS = 5 * 24 * UNA_HORA
const CLAVE_FICHAS_CERRADAS = 'fichasCerradas'

const ahora = ref(Date.now())
let intervaloAhora: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  intervaloAhora = setInterval(() => (ahora.value = Date.now()), 30000)
})
onBeforeUnmount(() => {
  if (intervaloAhora !== undefined) clearInterval(intervaloAhora)
})

const fichasCerradas = ref<number[]>(JSON.parse(localStorage.getItem(CLAVE_FICHAS_CERRADAS) || '[]'))
const fichasPospuestas = ref<number[]>([])
const turnosConDevolucion = ref<number[]>([])
const devolucionesCargadas = ref(false)

async function cargarTurnosConDevolucion() {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/devoluciones/turnos-con-devolucion`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (res.ok) turnosConDevolucion.value = await res.json()
  } finally {
    devolucionesCargadas.value = true
  }
}

onMounted(cargarTurnosConDevolucion)

function turnoTerminado(t: TurnoMedico) {
  const fin = new Date(t.fecha_hora).getTime() + UNA_HORA
  return t.estado?.estado === 'aceptado' && fin <= ahora.value && ahora.value - fin <= CINCO_DIAS
}

const turnoPopup = computed(() => {
  if (!devolucionesCargadas.value) return null
  const ocultos = [...fichasCerradas.value, ...fichasPospuestas.value, ...turnosConDevolucion.value]
  return ordenarPorFecha(turnos.value.filter(turnoTerminado)).reverse().find((t) => !ocultos.includes(t.id_turno)) ?? null
})

function inicialesPaciente(t: TurnoMedico) {
  return `${t.paciente.nombre.charAt(0)}${t.paciente.apellido.charAt(0)}`.toUpperCase()
}

function especialidadTurno(t: TurnoMedico) {
  const especialidad = t.especialidad?.nombre_especialidad
  return especialidad ? especialidad.charAt(0).toUpperCase() + especialidad.slice(1).toLowerCase() : 'Consulta'
}

function fechaLarga(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()} de ${nombresMes[f.getMonth()].toLowerCase()} de ${f.getFullYear()}`
}

const TIPOS_FICHA = ['application/pdf', 'image/jpeg', 'image/png']
const TAMANO_MAXIMO_FICHA = 10 * 1024 * 1024

const textoFicha = ref('')
const archivoFicha = ref<File | null>(null)
const errorFicha = ref('')
const guardandoFicha = ref(false)

function limpiarFicha() {
  textoFicha.value = ''
  archivoFicha.value = null
  errorFicha.value = ''
}

function elegirArchivoFicha(evento: Event) {
  const archivo = (evento.target as HTMLInputElement).files?.[0]
  if (!archivo) return
  if (!TIPOS_FICHA.includes(archivo.type)) {
    errorFicha.value = 'El archivo tiene que ser PDF, JPG o PNG.'
    return
  }
  if (archivo.size > TAMANO_MAXIMO_FICHA) {
    errorFicha.value = 'El archivo no puede superar los 10 MB.'
    return
  }
  archivoFicha.value = archivo
  errorFicha.value = ''
}

async function guardarFicha() {
  if (!turnoPopup.value) return
  if (!textoFicha.value.trim() && !archivoFicha.value) {
    errorFicha.value = 'Escribí la devolución o subí un archivo.'
    return
  }

  const idTurno = turnoPopup.value.id_turno
  const datos = new FormData()
  datos.append('id_turno', String(idTurno))
  if (textoFicha.value.trim()) datos.append('contenido', textoFicha.value)
  if (archivoFicha.value) datos.append('archivo', archivoFicha.value)

  guardandoFicha.value = true
  errorFicha.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/devoluciones`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${sesion.token}` },
      body: datos,
    })
    if (!res.ok) {
      const data = await res.json()
      errorFicha.value = data.detail || 'No se pudo guardar la devolución.'
      return
    }
    turnosConDevolucion.value.push(idTurno)
    limpiarFicha()
  } catch {
    errorFicha.value = 'No se pudo conectar con el servidor.'
  } finally {
    guardandoFicha.value = false
  }
}

function cerrarFicha() {
  if (!turnoPopup.value) return
  fichasCerradas.value.push(turnoPopup.value.id_turno)
  localStorage.setItem(CLAVE_FICHAS_CERRADAS, JSON.stringify(fichasCerradas.value))
  limpiarFicha()
}

function posponerFicha() {
  if (turnoPopup.value) fichasPospuestas.value.push(turnoPopup.value.id_turno)
  limpiarFicha()
}
</script>

<template>
  <div>
    <div class="navbar">
      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-mis-pacientes')">Mis pacientes<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+<span class="campoo-indicador"></span></button>
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
            <div class="dropdown-rol">Cuenta de médico</div>
          </div>
          <div class="dropdown-divisor"></div>


          <button @click="emit('ir-a-configuracion')">
            <div class="dropdown-item dropdown-item-destacado">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
              Configuración
            </div>
          </button>

          <button @click="emit('ir-a-bienvenida')">
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

    <div v-if="turnoPopup" class="fixed inset-0 z-200 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 font-['Inter']" @click.self="posponerFicha">
      <div :key="turnoPopup.id_turno" class="relative w-147.5 h-144.5 bg-white rounded-3xl shadow-[0_0.75rem_2rem_-0.5rem_rgba(20,51,87,0.1)] p-6">
        <button type="button" aria-label="Cerrar" class="absolute top-6 right-6 size-8 rounded-xl bg-[#F4F7FB] text-[#176FB7] flex items-center justify-center cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="cerrarFicha">
          <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
        </button>

        <div class="w-full h-full flex flex-col gap-4">
          <div class="flex flex-col gap-0.5">
            <div class="text-[#176FB7] text-[0.625rem] font-semibold leading-5">FICHA MÉDICA PENDIENTE</div>
            <div class="text-zinc-900 text-xl font-semibold leading-8">Completá la ficha del turno</div>
            <div class="text-[#61718B] text-[0.825rem] font-normal leading-5">Retomá el registro de tu última consulta.</div>
          </div>
          <div class="w-full h-20 px-4 bg-[#EDF5FF] rounded-xl flex items-center gap-4">
            <div class="size-11 shrink-0 bg-white rounded-3xl flex justify-center items-center">
              <div class="text-[#176FB7] text-base font-semibold leading-5">{{ inicialesPaciente(turnoPopup) }}</div>
            </div>
            <div class="flex-1 min-w-0 flex flex-col gap-1">
              <div class="text-zinc-900 text-base font-semibold leading-5 truncate">{{ nombrePaciente(turnoPopup) }}</div>
              <div class="text-[#61718B] text-[0.625rem] font-normal leading-5 truncate">{{ especialidadTurno(turnoPopup) }}</div>
            </div>
            <div class="shrink-0 flex flex-col gap-1 mr-15">
              <div class="text-zinc-900 text-[0.825rem] font-semibold leading-5">{{ fechaLarga(turnoPopup.fecha_hora) }}</div>
              <div class="text-[#61718B] text-[0.725rem] font-normal leading-5">{{ formatearHora(turnoPopup.fecha_hora) }} · Turno finalizado</div>
            </div>
          </div>

          <form class="flex-1 min-h-0 flex flex-col gap-4" @submit.prevent="guardarFicha">
            <div class="flex-1 min-h-0 flex flex-col gap-2">
              <div class="flex justify-between items-center">
                <label for="ficha" class="text-[#182234] text-[0.95rem] font-semibold leading-5">Escribir ficha médica</label>
                <span class="text-[#61718B] text-[0.725rem] font-normal leading-5">La va a ver el paciente</span>
              </div>
              <textarea id="ficha" v-model="textoFicha" name="ficha" placeholder="Escribí la evolución de la consulta, observaciones e indicaciones para el seguimiento del paciente…" class="flex-1 min-h-0 w-full p-3 rounded-xl bg-white border border-[#D7E2F0] text-sm text-zinc-900 placeholder:text-xs placeholder:text-[#61718B] resize-none focus:outline-none focus:border-[#176FB7]"></textarea>
            </div>
            <label class="relative w-full h-20 shrink-0 px-5 bg-[#F4F7FB] rounded-xl border border-dashed border-[#D7E2F0] flex items-center gap-4 cursor-pointer">
              <input type="file" name="archivo" accept=".pdf,.jpg,.jpeg,.png" class="absolute inset-0 opacity-0 cursor-pointer" @change="elegirArchivoFicha" />
              <svg class="shrink-0 text-[#176FB7]" style="width: 1.5rem; height: 1.5rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
              <div class="flex-1 min-w-0 flex flex-col gap-1">
                <span class="text-zinc-900 text-[0.95rem] font-semibold leading-5 truncate">O subí una ficha ya preparada</span>
                <span class="text-[#61718B] text-xs font-normal leading-5 truncate">{{ archivoFicha ? archivoFicha.name : 'Arrastrá un archivo PDF, JPG o PNG · Hasta 10 MB' }}</span>
              </div>
              <span class="shrink-0 text-[#176FB7] text-sm font-medium">Elegir archivo</span>
            </label>
            <p v-if="errorFicha" class="shrink-0 text-xs text-red-600">{{ errorFicha }}</p>
            <div class="shrink-0 flex justify-between gap-3">
              <button type="button" class="w-44 h-11 rounded-xl bg-[#F4F7FB] text-[#176FB7] text-sm font-medium cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="posponerFicha">Completar después</button>
              <button type="submit" :disabled="guardandoFicha" class="w-52 h-11 rounded-xl bg-[#4270B0] text-white text-sm font-medium cursor-pointer hover:bg-[#365E96] transition-colors disabled:opacity-60">{{ guardandoFicha ? 'Guardando...' : 'Guardar ficha médica' }}</button>
            </div>
          </form>

        </div>
      </div>
    </div>

    <div class="pm-contenido min-h-screen pt-[4.9rem] flex flex-col font-['Inter']">
      <div class="max-w-328 w-full mx-auto px-4 sm:px-8 pt-10 pb-10 flex flex-col gap-6">
        <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-4xl font-semibold text-gray-800">Bienvenido, {{ nombreUsuario }}</h1>
            <p class="text-base text-slate-500 mt-1.5">{{ fechaCorta(hoy) }} de {{ hoy.getFullYear() }}</p>
          </div>
          <button class="h-12 sm:w-64 px-6 rounded-2xl bg-linear-to-r from-sky-500 to-sky-700 text-white text-base font-medium cursor-pointer hover:opacity-90 transition-opacity" @click="emit('ir-a-solicitudes')">Ver solicitudes</button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr_32rem] gap-7">
          <div class="min-h-0 min-w-0 flex flex-col gap-6">
            <div class="shrink-0 grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div class="bg-white rounded-3xl shadow-[0_0.75rem_2rem_-0.5rem_rgba(20,51,87,0.1)] p-6 flex flex-col gap-3">
                <div class="flex items-center gap-2.5 text-base font-medium text-slate-500">
                  <svg style="width: 1.25rem; height: 1.25rem" class="text-sky-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></svg>
                  Turnos de hoy
                </div>
                <template v-if="turnosHoy.length">
                  <div class="flex items-center gap-2">
                    <span class="text-4xl font-semibold text-gray-800">{{ turnosHoyPendientes }}</span>
                    <span class="text-base text-slate-500">de {{ turnosHoy.length }} pendientes</span>
                  </div>
                  <div class="h-1.5 bg-indigo-50 rounded-full overflow-hidden">
                    <div class="h-full bg-sky-700 rounded-full transition-all" :style="{ width: `${progresoHoy}%` }"></div>
                  </div>
                </template>
                <p v-else class="text-base text-slate-500">No tenés turnos hoy.</p>
              </div>

              <div class="bg-white rounded-3xl shadow-[0_0.75rem_2rem_-0.5rem_rgba(20,51,87,0.1)] p-6 flex flex-col gap-2 min-w-0">
                <div class="flex items-center gap-2.5 text-base font-medium text-slate-500">
                  <svg style="width: 1.25rem; height: 1.25rem" class="text-sky-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></svg>
                  Próximo turno
                </div>
                <template v-if="proximoTurno">
                  <span class="text-4xl font-semibold text-gray-800">{{ formatearHora(proximoTurno.fecha_hora) }}</span>
                  <span class="text-xs text-slate-500 truncate">
                    <template v-if="!esMismoDia(proximoTurno.fecha_hora, hoy)">{{ formatearFecha(proximoTurno.fecha_hora) }} · </template>{{ nombrePaciente(proximoTurno) }}<template v-if="proximoTurno.notas"> · {{ proximoTurno.notas }}</template>
                  </span>
                </template>
                <p v-else class="text-base text-slate-500">Sin turnos próximos.</p>
              </div>
            </div>

            <div class="flex-1 min-h-0 bg-white rounded-3xl shadow-[0_0.75rem_2rem_-0.5rem_rgba(20,51,87,0.1)] p-7 flex flex-col gap-4">
              <div class="shrink-0 flex items-center gap-3">
                <svg style="width: 1.25rem; height: 1.25rem" class="text-sky-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></svg>
                <span class="text-xl font-semibold text-gray-800">{{ turnosHoy.length ? 'Agenda de hoy' : 'Próximos turnos' }}</span>
                <span class="px-3 h-7 rounded-2xl bg-blue-50 text-xs font-medium text-sky-700 flex items-center">{{ agenda.length }} turno{{ agenda.length !== 1 ? 's' : '' }}</span>
              </div>

              <p v-if="!agenda.length" class="text-sm text-slate-500">No tenés turnos próximos.</p>

              <div v-else class="max-h-40 flex flex-col overflow-y-auto">
                <button v-for="(t, i) in agenda" :key="t.id_turno" class="shrink-0 h-20 flex items-center gap-5 px-2 rounded-2xl text-left cursor-pointer hover:bg-slate-50 transition-colors" :class="{ 'opacity-50': yaPaso(t) }" @click="alHacerClick(t.fecha_hora)">
                  <div class="w-20 shrink-0 flex flex-col">
                    <span v-if="!turnosHoy.length" class="text-xs text-slate-500">{{ formatearFecha(t.fecha_hora) }}</span>
                    <span class="text-2xl font-medium text-gray-800">{{ formatearHora(t.fecha_hora) }}</span>
                  </div>
                  <div class="w-1 h-11 shrink-0 rounded-xs" :class="coloresTurno[i % coloresTurno.length]"></div>
                  <div class="flex-1 min-w-0 flex flex-col gap-0.75">
                    <span class="text-lg font-medium text-gray-800 truncate">{{ nombrePaciente(t) }}</span>
                    <span class="text-sm text-slate-500 truncate">{{ t.notas || 'Sin motivo especificado' }}</span>
                  </div>
                  <span class="text-2xl text-slate-500">›</span>
                </button>
              </div>

              <div class="mt-auto shrink-0 h-9 bg-slate-50 rounded-[10px] flex items-center justify-center text-xs text-slate-500">{{ turnosHoy.length ? 'Estos son tus turnos de hoy.' : 'Estos son tus próximos turnos.' }}</div>
            </div>
          </div>

          <div class="bg-white rounded-3xl shadow-[0_0.75rem_2rem_-0.5rem_rgba(20,51,87,0.1)] p-6 flex flex-col gap-4">
            <div class="shrink-0 flex items-center justify-between">
              <span class="text-2xl font-semibold text-gray-800">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
              <div class="flex gap-2">
                <button class="size-9 rounded-2xl bg-slate-50 outline-1 -outline-offset-1 outline-slate-200 text-base font-medium text-gray-800 flex items-center justify-center cursor-pointer hover:bg-slate-100 transition-colors" @click="mesAnterior">‹</button>
                <button class="size-9 rounded-2xl bg-slate-50 outline-1 -outline-offset-1 outline-slate-200 text-base font-medium text-gray-800 flex items-center justify-center cursor-pointer hover:bg-slate-100 transition-colors" @click="mesSiguiente">›</button>
              </div>
            </div>

            <div class="shrink-0 grid grid-cols-7">
              <div v-for="d in ['LU', 'MA', 'MI', 'JU', 'VI', 'SA', 'DO']" :key="d" class="h-7 flex items-center justify-center text-xs font-semibold text-slate-500">{{ d }}</div>
            </div>

            <div class="grid grid-cols-7 gap-y-1">
              <button v-for="(celda, i) in celdas" :key="i" class="h-8 rounded-2xl flex flex-col items-center justify-center gap-0.5 text-base transition-colors" :class="celda.otroMes ? 'text-gray-400 cursor-default' : celda.seleccionado ? 'bg-sky-700 text-white font-semibold' : celda.hoy ? 'text-sky-700 font-semibold hover:bg-slate-100 cursor-pointer' : 'text-gray-800 hover:bg-slate-100 cursor-pointer'" :disabled="celda.otroMes" @click="seleccionarDia(celda.fecha)">
                {{ celda.dia }}
                <span class="size-1 rounded-full" :class="celda.conTurno ? (celda.seleccionado ? 'bg-white' : 'bg-sky-700') : 'bg-transparent'"></span>
              </button>
            </div>

            <div class="shrink-0 p-3.5 bg-slate-50 rounded-2xl flex flex-col gap-1">
              <span class="text-sm font-semibold text-gray-800">{{ fechaCorta(seleccionado) }}</span>
              <span class="text-xs text-slate-500">{{ turnosSeleccionado ? `${turnosSeleccionado} turno${turnosSeleccionado !== 1 ? 's' : ''} programado${turnosSeleccionado !== 1 ? 's' : ''}` : 'Sin turnos programados' }}</span>
            </div>

            <button class="shrink-0 h-12 rounded-2xl bg-linear-to-r from-sky-500 to-sky-700 text-white text-base font-medium cursor-pointer hover:opacity-90 transition-opacity" @click="emit('ir-a-calendario')">Ver calendario completo →</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pm-contenido {
  background: linear-gradient(90deg, #9ac5f2 0%, #e7eef7 50%, #cae2f3 100%);
}
</style>
