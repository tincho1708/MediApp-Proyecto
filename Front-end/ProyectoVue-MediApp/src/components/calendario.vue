<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTurnosMedico, type TurnoMedico } from '@/stores/turnosMedico'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal', 'ir-a-chatbot', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-mis-pacientes', 'ir-a-configuracion'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const { turnos, usarPollingTurnos, guardarNotasMedico } = useTurnosMedico()

usarPollingTurnos()

const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const nombresDia = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

const hoy = new Date()
const mesActual = ref(hoy.getMonth())
const añoActual = ref(hoy.getFullYear())
const seleccionado = ref(hoy)

function esMismoDia(fecha: string | Date, dia: Date) {
  const f = new Date(fecha)
  return f.getFullYear() === dia.getFullYear() && f.getMonth() === dia.getMonth() && f.getDate() === dia.getDate()
}

function seleccionarDia(dia: Date) {
  seleccionado.value = dia
  mesActual.value = dia.getMonth()
  añoActual.value = dia.getFullYear()
}

function correrDias(n: number) {
  return new Date(seleccionado.value.getFullYear(), seleccionado.value.getMonth(), seleccionado.value.getDate() + n)
}

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

const turnosAceptados = computed(() => turnos.value.filter((t) => t.estado?.estado === 'aceptado'))

const celdas = computed(() => {
  const ultimoDia = new Date(añoActual.value, mesActual.value + 1, 0).getDate()
  const offset = (new Date(añoActual.value, mesActual.value, 1).getDay() + 6) % 7
  const resultado = []

  for (let i = -offset + 1; i <= ultimoDia || resultado.length % 7 !== 0; i++) {
    const fecha = new Date(añoActual.value, mesActual.value, i)
    resultado.push({
      fecha,
      otroMes: fecha.getMonth() !== mesActual.value,
      seleccionado: esMismoDia(fecha, seleccionado.value),
      conTurno: turnosAceptados.value.some((t) => esMismoDia(t.fecha_hora, fecha)),
    })
  }

  return resultado
})

const turnosDelDia = computed(() =>
  turnosAceptados.value.filter((t) => esMismoDia(t.fecha_hora, seleccionado.value)).sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime()),
)

const diasVecinos = computed(() => [correrDias(-1), seleccionado.value, correrDias(1)])

function formatearHora(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${String(f.getHours()).padStart(2, '0')}:${String(f.getMinutes()).padStart(2, '0')}`
}

function formatearFechaNumerica(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${String(f.getDate()).padStart(2, '0')}/${String(f.getMonth() + 1).padStart(2, '0')}/${f.getFullYear()}`
}

function fechaCorta(d: Date) {
  return `${nombresDia[d.getDay()]} ${d.getDate()} de ${nombresMes[d.getMonth()].toLowerCase()}`
}

function cantidadTurnos(n: number) {
  return `${n} turno${n !== 1 ? 's' : ''}`
}

function nombrePaciente(t: TurnoMedico) {
  return `${t.paciente.nombre} ${t.paciente.apellido}`
}

function iniciales(t: TurnoMedico) {
  return `${t.paciente.nombre.charAt(0)}${t.paciente.apellido.charAt(0)}`.toUpperCase()
}

const turnoEditandoId = ref<number | null>(null)
const notas = ref('')
const guardando = ref(false)
const errorGuardar = ref('')

const turnoEditando = computed(() => turnos.value.find((t) => t.id_turno === turnoEditandoId.value) ?? null)

function editarTurno(t: TurnoMedico) {
  turnoEditandoId.value = t.id_turno
  notas.value = t.notas_medico ?? ''
  errorGuardar.value = ''
}

function cerrarEdicion() {
  turnoEditandoId.value = null
}

async function guardarCambios() {
  if (!turnoEditando.value) return
  guardando.value = true
  errorGuardar.value = ''
  try {
    await guardarNotasMedico(turnoEditando.value.id_turno, notas.value)
    cerrarEdicion()
  } catch (e) {
    errorGuardar.value = e instanceof Error ? e.message : 'No se pudo conectar al servidor.'
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <div>
    <div class="navbar">
      <button @click="emit('ir-a-principal')">
        <div class="navbar-logo">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

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

    <div class="min-h-screen lg:h-screen lg:overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
      <div class="flex-1 min-h-0 max-w-328 w-full mx-auto px-4 sm:px-8 pt-8 pb-6 flex flex-col gap-6">
        <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div v-if="turnoEditando">
            <h1 class="text-3xl font-semibold text-gray-800">Editar turno</h1>
            <p class="text-sm text-slate-500 mt-2">Agregá notas privadas sobre la consulta. Solo vos podés verlas.</p>
          </div>
          <div v-else>
            <h1 class="text-3xl font-semibold text-gray-800">Calendario</h1>
            <p class="text-sm text-slate-500 mt-2">Consultá tus turnos y organizá cada día de atención.</p>
          </div>
          <button v-if="turnoEditando" class="h-11 px-5 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center justify-center gap-2 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="cerrarEdicion">
            <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
            Volver al calendario
          </button>
          <button v-else class="h-11 px-6 bg-[#3D6FC2] rounded-xl text-sm font-medium text-white cursor-pointer hover:opacity-90 transition-opacity" @click="emit('ir-a-solicitudes')">Ver solicitudes</button>
        </div>

        <div class="lg:flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[20rem_1fr] lg:grid-rows-[minmax(0,1fr)] gap-6">
          <div class="min-h-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-5 flex flex-col gap-3">
            <div class="shrink-0 flex items-center justify-between">
              <span class="text-lg font-semibold text-gray-800">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
              <div class="flex gap-2">
                <button class="size-9 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="mesAnterior">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6" /></svg>
                </button>
                <button class="size-9 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="mesSiguiente">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6" /></svg>
                </button>
              </div>
            </div>

            <div class="flex-1 min-h-0 flex flex-col gap-1">
              <div class="shrink-0 grid grid-cols-7">
                <span v-for="d in ['LU', 'MA', 'MI', 'JU', 'VI', 'SA', 'DO']" :key="d" class="h-5 text-center text-xs text-slate-500">{{ d }}</span>
              </div>
              <div class="flex-1 min-h-0 grid grid-cols-7 auto-rows-[minmax(1.75rem,2.5rem)] content-start gap-0.5">
                <button v-for="celda in celdas" :key="celda.fecha.getTime()" class="rounded-xl flex flex-col items-center justify-center gap-0.5 text-sm font-medium cursor-pointer transition-colors" :class="celda.seleccionado ? 'bg-[#3D6FC2] text-white' : celda.otroMes ? 'text-slate-500 hover:bg-slate-50' : 'text-gray-800 hover:bg-slate-100'" @click="seleccionarDia(celda.fecha)">
                  {{ celda.fecha.getDate() }}
                  <span class="size-0.75 rounded-full" :class="celda.conTurno ? (celda.seleccionado ? 'bg-white' : 'bg-[#3D6FC2]') : 'bg-transparent'"></span>
                </button>
              </div>
            </div>

            <div class="shrink-0 flex items-center gap-2 text-xs text-slate-500">
              <span class="size-1.5 rounded-full bg-[#3D6FC2]"></span>
              Día con turnos
            </div>

            <div class="shrink-0 h-px bg-slate-200"></div>

            <div class="shrink-0 px-4 py-3 bg-blue-50 rounded-2xl flex flex-col gap-1">
              <span class="text-sm font-medium text-[#3D6FC2]">{{ fechaCorta(seleccionado) }}</span>
              <span class="text-base font-semibold text-gray-800">{{ turnosDelDia.length ? `${cantidadTurnos(turnosDelDia.length)} programado${turnosDelDia.length !== 1 ? 's' : ''}` : 'Sin turnos programados' }}</span>
              <span v-if="turnosDelDia.length" class="text-xs text-slate-500">Primer turno a las {{ formatearHora(turnosDelDia[0].fecha_hora) }}</span>
            </div>

            <button class="shrink-0 h-10 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="seleccionarDia(hoy)">Ir a hoy</button>
          </div>

          <div v-if="turnoEditando" class="min-h-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-6 flex flex-col gap-4">
            <div class="shrink-0 flex items-center justify-between gap-4">
              <span class="text-lg font-semibold text-gray-800">Datos del turno</span>
              <span class="text-xs text-slate-500">{{ fechaCorta(new Date(turnoEditando.fecha_hora)) }} de {{ new Date(turnoEditando.fecha_hora).getFullYear() }}</span>
            </div>

            <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-4">
              <div class="shrink-0 p-4 bg-slate-50 rounded-2xl flex items-center gap-4 min-w-0">
                <div class="size-11 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-sm font-medium flex items-center justify-center">{{ iniciales(turnoEditando) }}</div>
                <div class="min-w-0">
                  <div class="text-lg font-semibold text-gray-800 truncate">{{ nombrePaciente(turnoEditando) }}</div>
                  <div class="text-xs text-slate-500 truncate">Email: {{ turnoEditando.paciente.mail }}</div>
                </div>
              </div>

              <div class="shrink-0 grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div class="flex flex-col gap-2">
                  <span class="text-sm font-medium text-gray-800">Fecha</span>
                  <span class="h-12 px-4 bg-slate-50 rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center text-sm text-gray-800">{{ formatearFechaNumerica(turnoEditando.fecha_hora) }}</span>
                </div>
                <div class="flex flex-col gap-2">
                  <span class="text-sm font-medium text-gray-800">Horario</span>
                  <span class="h-12 px-4 bg-slate-50 rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center text-sm text-gray-800">{{ formatearHora(turnoEditando.fecha_hora) }}</span>
                </div>
              </div>

              <div class="shrink-0 flex flex-col gap-2">
                <span class="text-sm font-medium text-gray-800">Motivo de la consulta</span>
                <span class="min-h-12 px-4 py-3 bg-slate-50 rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center text-sm text-gray-800 wrap-break-word">{{ turnoEditando.notas || 'Sin motivo especificado' }}</span>
              </div>

              <label class="flex-1 min-h-40 flex flex-col gap-2">
                <span class="shrink-0 flex items-baseline gap-2">
                  <span class="text-sm font-medium text-gray-800">Notas</span>
                  <span class="text-xs text-slate-500">Opcional · solo las ves vos</span>
                </span>
                <textarea v-model="notas" placeholder="Agregá una nota sobre este turno…" class="flex-1 min-h-32 w-full p-4 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 focus:outline-[#3D6FC2] text-sm text-gray-800 placeholder:text-slate-500 resize-none"></textarea>
              </label>
            </div>

            <div class="shrink-0 flex flex-col gap-2">
              <p v-if="errorGuardar" class="text-sm text-red-600">{{ errorGuardar }}</p>
              <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
                <button class="sm:w-32 h-12 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="cerrarEdicion">Descartar cambios</button>
                <button class="sm:w-60 h-12 bg-[#3D6FC2] rounded-xl flex items-center justify-center gap-2 text-sm font-medium text-white cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed" :disabled="guardando" @click="guardarCambios">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
                  {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
                </button>
              </div>
              <span class="text-xs text-slate-500">Los cambios se aplican al guardar.</span>
            </div>
          </div>

          <div v-else class="min-h-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-6 flex flex-col gap-6">
            <div class="shrink-0 flex items-center justify-between gap-4">
              <div>
                <div class="text-lg font-semibold text-gray-800">Agenda del día</div>
                <div class="text-sm text-slate-500">{{ fechaCorta(seleccionado) }} de {{ seleccionado.getFullYear() }}</div>
              </div>
              <div class="flex gap-2">
                <button class="size-11 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="seleccionarDia(correrDias(-1))">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6" /></svg>
                </button>
                <button class="w-18 h-11 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="seleccionarDia(hoy)">Hoy</button>
                <button class="size-11 rounded-xl bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2] flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors" @click="seleccionarDia(correrDias(1))">
                  <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6" /></svg>
                </button>
              </div>
            </div>

            <div class="shrink-0 grid grid-cols-3 gap-3">
              <button v-for="(dia, i) in diasVecinos" :key="i" class="h-20 p-4 rounded-2xl flex items-center gap-3 text-left cursor-pointer transition-colors min-w-0" :class="i === 1 ? 'bg-blue-50 outline-1 -outline-offset-1 outline-[#3D6FC2]' : 'bg-slate-50 hover:bg-slate-100'" @click="seleccionarDia(dia)">
                <span class="text-3xl font-semibold" :class="i === 1 ? 'text-[#3D6FC2]' : 'text-slate-500'">{{ dia.getDate() }}</span>
                <span class="hidden sm:flex flex-col min-w-0">
                  <span class="text-sm font-medium truncate" :class="i === 1 ? 'text-[#3D6FC2]' : 'text-slate-500'">{{ nombresDia[dia.getDay()] }}</span>
                  <span class="text-xs text-slate-500 truncate">{{ nombresMes[dia.getMonth()] }} de {{ dia.getFullYear() }}</span>
                </span>
              </button>
            </div>

            <div class="flex-1 min-h-0 flex flex-col gap-4">
              <div class="shrink-0 flex items-center justify-between">
                <span class="text-sm font-medium text-gray-800">Turnos programados</span>
                <span class="text-xs text-slate-500">{{ cantidadTurnos(turnosDelDia.length) }}</span>
              </div>

              <div v-if="turnosDelDia.length" class="min-h-0 max-h-55 overflow-y-auto flex flex-col gap-3 pr-1">
                <div v-for="t in turnosDelDia" :key="t.id_turno" class="shrink-0 h-26 px-6 bg-blue-50 rounded-2xl outline-1 -outline-offset-1 outline-slate-200 flex items-center gap-6 min-w-0">
                  <div class="shrink-0 flex flex-col">
                    <span class="text-2xl font-semibold text-[#3D6FC2]">{{ formatearHora(t.fecha_hora) }}</span>
                    <span class="text-xs text-slate-500">Horario</span>
                  </div>
                  <div class="w-px h-14 shrink-0 bg-slate-200"></div>
                  <div class="flex-1 min-w-0 flex flex-col gap-2">
                    <span class="text-lg font-semibold text-gray-800 truncate">{{ nombrePaciente(t) }}</span>
                    <span class="text-sm text-slate-500 truncate">{{ t.notas || 'Sin motivo especificado' }}</span>
                  </div>
                  <button class="shrink-0 h-11 px-5 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center gap-2 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="editarTurno(t)">
                    <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4Z" /></svg>
                    Editar
                  </button>
                </div>
              </div>

              <div class="shrink-0 p-4 bg-slate-50 rounded-xl flex items-center gap-2 text-sm text-slate-500">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
                {{ turnosDelDia.length ? 'No hay más turnos programados para este día.' : 'No hay turnos programados para este día.' }}
              </div>
            </div>

            <p class="shrink-0 flex items-center gap-2 text-xs text-slate-500">
              <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9" /><path d="M12 16v-4M12 8h.01" /></svg>
              Usá "Editar" para ver los datos del turno y agregar notas.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
