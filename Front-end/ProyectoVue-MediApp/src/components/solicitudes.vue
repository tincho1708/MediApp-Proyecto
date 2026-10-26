<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useTurnosMedico, type TurnoMedico } from '@/stores/turnosMedico'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-mis-pacientes', 'ir-a-configuracion'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const { turnos, cargando, error: errorCarga, usarPollingTurnos, actualizarEstadoTurno } = useTurnosMedico()

usarPollingTurnos()

const busqueda = ref('')
const orden = ref<'recientes' | 'proximos'>('recientes')
const turnoSeleccionadoId = ref<number | null>(null)

const turnosPendientes = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  const filtrados = turnos.value.filter((t) => t.estado.estado === 'pendiente' && nombrePaciente(t).toLowerCase().includes(texto))
  const clave = (t: TurnoMedico) => (orden.value === 'recientes' ? -new Date(t.creado_en).getTime() : new Date(t.fecha_hora).getTime())
  return filtrados.sort((a, b) => clave(a) - clave(b))
})

const turnoSeleccionado = computed(() => turnosPendientes.value.find((t) => t.id_turno === turnoSeleccionadoId.value) ?? turnosPendientes.value[0] ?? null)

const nombresMes = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

function nombrePaciente(t: TurnoMedico) {
  return `${t.paciente.nombre} ${t.paciente.apellido}`
}

function iniciales(t: TurnoMedico) {
  return `${t.paciente.nombre.charAt(0)}${t.paciente.apellido.charAt(0)}`.toUpperCase()
}

function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()} de ${nombresMes[f.getMonth()]}`
}

function formatearRangoHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const fin = new Date(f.getTime() + 60 * 60 * 1000)
  const hora = (d: Date) => `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  return `${hora(f)}–${hora(fin)}`
}

function tiempoRelativo(creadoEn: string) {
  const minutos = Math.max(0, Math.floor((Date.now() - new Date(creadoEn + 'Z').getTime()) / 60000))
  if (minutos < 1) return 'unos segundos'
  if (minutos < 60) return `${minutos} minuto${minutos === 1 ? '' : 's'}`
  const horas = Math.floor(minutos / 60)
  if (horas < 24) return `${horas} hora${horas === 1 ? '' : 's'}`
  const dias = Math.floor(horas / 24)
  return `${dias} día${dias === 1 ? '' : 's'}`
}

const procesando = ref(false)
const errorAccion = ref('')

async function resolverTurno(accion: 'aceptar' | 'rechazar') {
  if (!turnoSeleccionado.value) return
  procesando.value = true
  errorAccion.value = ''
  try {
    await actualizarEstadoTurno(turnoSeleccionado.value.id_turno, accion)
    turnoSeleccionadoId.value = null
  } catch (e) {
    errorAccion.value = e instanceof Error ? e.message : 'No se pudo conectar al servidor.'
  } finally {
    procesando.value = false
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
        <button class="campoo activo">Solicitudes<span class="campoo-indicador"></span></button>
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
      <div class="flex-1 min-h-0 max-w-328 w-full mx-auto px-4 sm:px-8 pt-10 pb-8 flex flex-col gap-8">
        <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-3xl font-semibold text-gray-800">Solicitudes de turnos</h1>
            <p class="text-sm text-slate-500 mt-2">Revisá los pedidos de tus pacientes y organizá tu agenda.</p>
          </div>
          <button class="h-11 px-5 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center justify-center gap-2 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="emit('ir-a-calendario')">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></svg>
            Ver agenda
          </button>
        </div>

        <div class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[1fr_30.5rem] lg:grid-rows-[minmax(0,1fr)] gap-6">
          <div class="min-h-0 min-w-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-6 flex flex-col gap-4">
            <div class="shrink-0 flex items-center gap-3">
              <span class="text-lg font-semibold text-gray-800">Pendientes</span>
              <span class="h-7 px-3 rounded-xl bg-blue-50 text-xs text-[#3D6FC2] flex items-center">{{ turnosPendientes.length }} solicitud{{ turnosPendientes.length !== 1 ? 'es' : '' }}</span>
            </div>

            <div class="shrink-0 flex flex-col sm:flex-row gap-3">
              <label class="flex-1 h-11 px-3 bg-slate-50 rounded-xl flex items-center gap-3">
                <svg style="width: 1.25rem; height: 1.25rem" class="shrink-0 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
                <input v-model="busqueda" type="text" placeholder="Buscar paciente…" class="w-full bg-transparent text-sm text-gray-800 placeholder:text-slate-500 outline-none" />
              </label>
              <label class="relative sm:w-56 shrink-0">
                <select v-model="orden" class="w-full h-11 pl-3 pr-9 appearance-none bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-slate-500 cursor-pointer">
                  <option value="recientes">Más recientes primero</option>
                  <option value="proximos">Turno más próximo</option>
                </select>
                <svg style="width: 1rem; height: 1rem" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6" /></svg>
              </label>
            </div>

            <div class="shrink-0 hidden md:grid grid-cols-[14rem_1fr_11rem_1.25rem] gap-4 px-4 text-xs text-slate-500">
              <span>PACIENTE</span>
              <span>MOTIVO</span>
              <span>TURNO SOLICITADO</span>
            </div>

            <p v-if="cargando" class="text-sm text-slate-500">Cargando solicitudes...</p>
            <p v-else-if="errorCarga" class="text-sm text-red-600">{{ errorCarga }}</p>
            <p v-else-if="!turnosPendientes.length" class="text-sm text-slate-500">{{ busqueda ? 'No hay solicitudes de ese paciente.' : 'No tenés solicitudes pendientes.' }}</p>

            <div v-else class="flex-1 min-h-0 max-h-96 lg:max-h-none flex flex-col gap-2 overflow-y-auto">
              <button v-for="t in turnosPendientes" :key="t.id_turno" class="shrink-0 grid grid-cols-[1fr_auto_1.25rem] md:grid-cols-[14rem_1fr_11rem_1.25rem] items-center gap-4 px-4 py-3 rounded-2xl text-left cursor-pointer transition-colors" :class="turnoSeleccionado?.id_turno === t.id_turno ? 'bg-blue-50 outline-1 -outline-offset-1 outline-[#3D6FC2]' : 'hover:bg-slate-50'" @click="turnoSeleccionadoId = t.id_turno">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="size-11 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-sm font-medium flex items-center justify-center">{{ iniciales(t) }}</div>
                  <div class="min-w-0">
                    <div class="text-sm font-medium text-gray-800 truncate">{{ nombrePaciente(t) }}</div>
                    <div class="text-xs text-slate-500">Paciente</div>
                  </div>
                </div>
                <span class="hidden md:block text-sm text-slate-500 line-clamp-2">{{ t.notas || 'Sin motivo especificado' }}</span>
                <div>
                  <div class="text-sm font-medium text-gray-800">{{ formatearFecha(t.fecha_hora) }}</div>
                  <div class="text-xs text-slate-500">{{ formatearRangoHora(t.fecha_hora) }}</div>
                </div>
                <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6" /></svg>
              </button>
            </div>
          </div>

          <div class="min-h-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-6 flex flex-col gap-5">
            <span class="shrink-0 text-lg font-semibold text-gray-800">Detalle de la solicitud</span>

            <p v-if="!turnoSeleccionado" class="flex-1 flex items-center justify-center text-center text-sm text-slate-500">Cuando un paciente pida un turno, vas a ver el detalle acá.</p>

            <template v-else>
              <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-5">
              <div class="shrink-0 flex items-center gap-4 min-w-0">
                <div class="size-16 shrink-0 rounded-3xl bg-blue-50 text-[#3D6FC2] text-xl font-semibold flex items-center justify-center">{{ iniciales(turnoSeleccionado) }}</div>
                <span class="text-xl font-semibold text-gray-800 truncate">{{ nombrePaciente(turnoSeleccionado) }}</span>
              </div>

              <div class="shrink-0 p-4 bg-slate-50 rounded-2xl flex flex-col gap-2">
                <div class="flex items-center gap-2 text-sm font-medium text-slate-500">
                  <svg style="width: 1.25rem; height: 1.25rem" class="text-[#3D6FC2]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></svg>
                  Turno solicitado
                </div>
                <span class="text-lg font-semibold text-gray-800">{{ formatearFecha(turnoSeleccionado.fecha_hora) }} · {{ formatearRangoHora(turnoSeleccionado.fecha_hora) }}</span>
              </div>

              <div class="shrink-0 flex flex-col gap-3">
                <span class="text-sm font-medium text-gray-800">Motivo de la consulta</span>
                <p class="min-h-28 p-4 bg-slate-50 rounded-2xl text-sm text-gray-800 wrap-break-word">{{ turnoSeleccionado.notas || 'Sin motivo especificado' }}</p>
              </div>

              <div class="shrink-0 flex items-center gap-2 text-sm text-slate-500">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></svg>
                Recibida hace {{ tiempoRelativo(turnoSeleccionado.creado_en) }}
              </div>
              </div>

              <div class="shrink-0 flex flex-col gap-3">
                <p v-if="errorAccion" class="text-sm text-red-600">{{ errorAccion }}</p>
                <p class="text-xs text-slate-500">Revisá la fecha y el horario antes de confirmar.</p>
                <div class="flex gap-3">
                  <button class="flex-2 h-12 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 flex items-center justify-center gap-2 text-sm font-medium text-pink-700 cursor-pointer hover:bg-pink-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed" :disabled="procesando" @click="resolverTurno('rechazar')">
                    <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
                    Rechazar
                  </button>
                  <button class="flex-3 h-12 bg-[#3D6FC2] rounded-xl flex items-center justify-center gap-2 text-sm font-medium text-white cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed" :disabled="procesando" @click="resolverTurno('aceptar')">
                    <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
                    Aceptar turno
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
