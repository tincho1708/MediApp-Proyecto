<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useTurnosMedico, type TurnoMedico } from '@/stores/turnosMedico'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal', 'ir-a-chatbot', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-configuracion'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const { turnos, cargando, error, usarPollingTurnos } = useTurnosMedico()

usarPollingTurnos()

type Paciente = {
  id: number
  nombre: string
  apellido: string
  mail: string
  proximoTurno: TurnoMedico | null
  notaRapida: string | null
}

const busqueda = ref('')
const pacienteAbiertoId = ref<number | null>(null)

const tiempo = (t: TurnoMedico) => new Date(t.fecha_hora).getTime()

const pacientes = computed(() => {
  const ahora = Date.now()
  const porPaciente = new Map<number, TurnoMedico[]>()

  for (const t of turnos.value) {
    if (t.estado.estado !== 'aceptado') continue
    porPaciente.set(t.paciente.id, [...(porPaciente.get(t.paciente.id) ?? []), t])
  }

  return [...porPaciente.values()].map((lista): Paciente => {
    const ordenados = [...lista].sort((a, b) => tiempo(a) - tiempo(b))
    const conNota = [...ordenados].reverse().find((t) => t.notas_medico)
    return {
      ...ordenados[0].paciente,
      proximoTurno: ordenados.find((t) => tiempo(t) >= ahora) ?? null,
      notaRapida: conNota?.notas_medico ?? null,
    }
  })
})

const pacientesFiltrados = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  return pacientes.value
    .filter((p) => nombreCompleto(p).toLowerCase().includes(texto))
    .sort((a, b) => (a.proximoTurno ? tiempo(a.proximoTurno) : Infinity) - (b.proximoTurno ? tiempo(b.proximoTurno) : Infinity) || nombreCompleto(a).localeCompare(nombreCompleto(b)))
})

const pacienteAbierto = computed(() => pacientes.value.find((p) => p.id === pacienteAbiertoId.value) ?? null)

function nombreCompleto(p: { nombre: string; apellido: string }) {
  return `${p.nombre} ${p.apellido}`
}

function iniciales(p: { nombre: string; apellido: string }) {
  return `${p.nombre.charAt(0)}${p.apellido.charAt(0)}`.toUpperCase()
}

function formatearTurno(t: TurnoMedico) {
  const f = new Date(t.fecha_hora)
  const dos = (n: number) => String(n).padStart(2, '0')
  return `${dos(f.getDate())}/${dos(f.getMonth() + 1)}/${f.getFullYear()} · ${dos(f.getHours())}:${dos(f.getMinutes())}`
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
        <button class="campoo activo">Mis pacientes<span class="campoo-indicador"></span></button>
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
        <div class="shrink-0">
          <h1 class="text-3xl font-semibold text-gray-800">Mis pacientes</h1>
          <p class="text-sm text-slate-500 mt-2">Encontrá a tus pacientes y consultá sus datos y notas de un vistazo.</p>
        </div>

        <div class="lg:flex-1 min-h-0 bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] p-6 flex flex-col gap-4">
          <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="text-lg font-semibold text-gray-800">Todos los pacientes</span>
              <span class="h-7 px-3 rounded-xl bg-blue-50 text-xs text-[#3D6FC2] flex items-center">{{ pacientes.length }} paciente{{ pacientes.length !== 1 ? 's' : '' }}</span>
            </div>
            <label class="sm:w-96 h-11 px-3 bg-slate-50 rounded-xl flex items-center gap-3">
              <svg style="width: 1.25rem; height: 1.25rem" class="shrink-0 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
              <input v-model="busqueda" type="text" placeholder="Buscar por nombre…" class="w-full bg-transparent text-sm text-gray-800 placeholder:text-slate-500 outline-none" />
            </label>
          </div>

          <div class="shrink-0 hidden md:grid grid-cols-[minmax(10rem,16rem)_10rem_1fr_7rem] gap-6 px-4 text-xs text-slate-500">
            <span>PACIENTE</span>
            <span>PRÓXIMO TURNO</span>
            <span>NOTAS RÁPIDAS</span>
          </div>

          <p v-if="cargando" class="text-sm text-slate-500">Cargando pacientes...</p>
          <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
          <p v-else-if="!pacientesFiltrados.length" class="text-sm text-slate-500">{{ busqueda ? 'No hay pacientes con ese nombre.' : 'Todavía no tenés pacientes con turnos aceptados.' }}</p>

          <div v-else class="flex-1 min-h-0 overflow-y-auto">
            <button v-for="(p, i) in pacientesFiltrados" :key="p.id" class="w-full min-h-14 px-4 py-2 grid grid-cols-[1fr_auto] md:grid-cols-[minmax(10rem,16rem)_10rem_1fr_7rem] items-center gap-x-6 gap-y-1 border-b border-slate-200 text-left cursor-pointer transition-colors hover:bg-blue-50" :class="i % 2 ? 'bg-slate-50' : 'bg-white'" @click="pacienteAbiertoId = p.id">
              <span class="flex items-center gap-3 min-w-0">
                <span class="size-8 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-xs font-medium flex items-center justify-center">{{ iniciales(p) }}</span>
                <span class="text-sm font-medium text-gray-800 truncate">{{ nombreCompleto(p) }}</span>
              </span>
              <span class="hidden md:block text-sm text-slate-500">{{ p.proximoTurno ? formatearTurno(p.proximoTurno) : 'Sin turnos próximos' }}</span>
              <span class="hidden md:block text-sm text-gray-800 truncate">{{ p.notaRapida || 'Sin notas rápidas' }}</span>
              <span class="flex items-center justify-center gap-2 text-sm font-medium text-[#3D6FC2]">
                <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6" /></svg>
                Ver ficha
              </span>
              <span class="md:hidden col-span-2 text-xs text-slate-500">{{ p.proximoTurno ? formatearTurno(p.proximoTurno) : 'Sin turnos próximos' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pacienteAbierto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 font-['Inter']" @click="pacienteAbiertoId = null">
      <div class="bg-white rounded-3xl p-6 sm:p-8 w-lg max-w-full max-h-full overflow-y-auto flex flex-col gap-5" @click.stop>
        <div class="flex items-center gap-4 min-w-0">
          <div class="size-14 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-lg font-semibold flex items-center justify-center">{{ iniciales(pacienteAbierto) }}</div>
          <div class="min-w-0">
            <div class="text-xl font-semibold text-gray-800 truncate">{{ nombreCompleto(pacienteAbierto) }}</div>
            <div class="text-sm text-slate-500 truncate">{{ pacienteAbierto.mail }}</div>
          </div>
        </div>

        <div class="p-4 bg-slate-50 rounded-2xl flex flex-col gap-2">
          <div class="flex items-center gap-2 text-sm font-medium text-slate-500">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-[#3D6FC2]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></svg>
            Próximo turno
          </div>
          <span class="text-lg font-semibold text-gray-800">{{ pacienteAbierto.proximoTurno ? formatearTurno(pacienteAbierto.proximoTurno) : 'Sin turnos próximos' }}</span>
        </div>

        <div v-if="pacienteAbierto.proximoTurno" class="flex flex-col gap-2">
          <span class="text-sm font-medium text-gray-800">Motivo de la consulta</span>
          <p class="p-4 bg-slate-50 rounded-2xl text-sm text-gray-800 wrap-break-word">{{ pacienteAbierto.proximoTurno.notas || 'El paciente no dejó un motivo para este turno.' }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <span class="text-sm font-medium text-gray-800">Notas rápidas</span>
          <p class="p-4 bg-slate-50 rounded-2xl text-sm text-gray-800 wrap-break-word">{{ pacienteAbierto.notaRapida || 'Todavía no agregaste notas sobre este paciente.' }}</p>
        </div>

        <button class="h-11 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors" @click="pacienteAbiertoId = null">Cerrar</button>
      </div>
    </div>
  </div>
</template>
