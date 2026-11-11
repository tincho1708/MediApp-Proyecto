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
  telefono: string | null
  ciudad: string | null
  foto: string | null
  proximoTurno: TurnoMedico | null
  notaRapida: string | null
  primerTurno: string
}

type Devolucion = {
  id: number
  id_turno: number | null
  contenido: string | null
  archivo_nombre: string | null
  fecha: string
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
      primerTurno: ordenados[0].fecha_hora,
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

// pop up
const API = import.meta.env.VITE_API_URL
const headers = { Authorization: `Bearer ${sesion.token}` }
const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

const devoluciones = ref<Devolucion[]>([])
const busquedaFichas = ref('')
const fichaAbierta = ref<number | null>(null)
const errorDescarga = ref('')

onMounted(async () => {
  const res = await fetch(`${API}/devoluciones/enviadas`, { headers })
  if (res.ok) devoluciones.value = await res.json()
})

function abrirPaciente(id: number) {
  pacienteAbiertoId.value = id
  busquedaFichas.value = ''
  fichaAbierta.value = null
  errorDescarga.value = ''
}

function pacienteDesde(p: Paciente) {
  const f = new Date(p.primerTurno)
  return `${meses[f.getMonth()]} de ${f.getFullYear()}`
}

function fechaLarga(t: TurnoMedico) {
  const f = new Date(t.fecha_hora)
  return `${f.getDate()} de ${meses[f.getMonth()]} de ${f.getFullYear()} · ${formatearTurno(t).split(' · ')[1]}`
}

function fechaRegistro(d: Devolucion) {
  return new Date(`${d.fecha}Z`).toLocaleDateString('es-AR')
}

function especialidadTurno(t: TurnoMedico) {
  return t.especialidad?.nombre_especialidad ?? 'Consulta'
}

function tipoFicha(d: Devolucion) {
  if (d.contenido && d.archivo_nombre) return 'Ficha escrita y archivo'
  return d.archivo_nombre ? 'Ficha adjunta' : 'Ficha escrita'
}

const fichasPaciente = computed(() =>
  turnos.value
    .filter((t) => t.paciente.id === pacienteAbiertoId.value && t.estado.estado === 'aceptado' && tiempo(t) < Date.now())
    .sort((a, b) => tiempo(b) - tiempo(a))
    .map((turno) => ({ turno, devolucion: devoluciones.value.find((d) => d.id_turno === turno.id_turno) })),
)

const fichasFiltradas = computed(() =>
  fichasPaciente.value.filter(({ turno, devolucion }) =>
    `${fechaLarga(turno)} ${formatearTurno(turno)} ${especialidadTurno(turno)} ${devolucion?.contenido ?? ''}`
      .toLowerCase()
      .includes(busquedaFichas.value.trim().toLowerCase()),
  ),
)

const cantidadFichas = computed(() => fichasPaciente.value.filter((f) => f.devolucion).length)

const datosPaciente = computed(() => [
  { titulo: 'Teléfono', valor: pacienteAbierto.value?.telefono || 'No informado' },
  { titulo: 'Ciudad', valor: pacienteAbierto.value?.ciudad || 'No informada' },
  { titulo: 'Último turno', valor: fichasPaciente.value[0] ? formatearTurno(fichasPaciente.value[0].turno) : 'Sin turnos anteriores' },
  { titulo: 'Turnos anteriores', valor: fichasPaciente.value.length },
])

async function descargarArchivo(d: Devolucion) {
  errorDescarga.value = ''
  const res = await fetch(`${API}/devoluciones/${d.id}/archivo`, { headers }).catch(() => null)
  if (!res?.ok) {
    errorDescarga.value = 'No se pudo descargar el archivo. Intentá de nuevo.'
    return
  }
  const enlace = document.createElement('a')
  enlace.href = URL.createObjectURL(await res.blob())
  enlace.download = d.archivo_nombre ?? 'ficha'
  enlace.click()
  URL.revokeObjectURL(enlace.href)
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
          <Avatar propia class="navbar-usuario-avatar" :texto="nombreUsuario.charAt(0).toUpperCase()" />
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

    <div v-show="!pacienteAbierto" class="min-h-screen lg:h-screen lg:overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
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
            <button v-for="(p, i) in pacientesFiltrados" :key="p.id" class="w-full min-h-14 px-4 py-2 grid grid-cols-[1fr_auto] md:grid-cols-[minmax(10rem,16rem)_10rem_1fr_7rem] items-center gap-x-6 gap-y-1 border-b border-slate-200 text-left cursor-pointer transition-colors hover:bg-blue-50" :class="i % 2 ? 'bg-slate-50' : 'bg-white'" @click="abrirPaciente(p.id)">
              <span class="flex items-center gap-3 min-w-0">
                <Avatar class="size-8 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-xs font-medium flex items-center justify-center" :foto="p.foto" :texto="iniciales(p)" />
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

    <!-- pop up -->
    <div v-if="pacienteAbierto" class="fixed inset-x-0 bottom-0 top-[4.9rem] z-50 overflow-y-auto lg:overflow-hidden bg-[linear-gradient(135deg,#bfdbfe_0%,#ffffff_50%,#bfdbfe_100%)] font-['Inter']">
      <div class="lg:h-full px-4 sm:px-16 py-6 flex flex-col gap-5">
        <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-3xl font-semibold text-[#182234]">Información del paciente</h1>
            <p class="text-sm text-[#61718B] mt-1">Datos personales y fichas médicas de sus turnos anteriores.</p>
          </div>
          <button class="shrink-0 h-11 px-6 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="pacienteAbiertoId = null">← Volver a mis pacientes</button>
        </div>

        <div class="lg:flex-1 lg:min-h-0 flex flex-col lg:flex-row gap-6">
          <section class="lg:w-88 shrink-0 p-6 bg-white rounded-2xl shadow-[0_0.25rem_1rem_0_rgba(26,51,89,0.08)] flex flex-col justify-between gap-4 lg:overflow-y-auto">
            <div class="flex flex-col gap-4">
              <Avatar class="size-16 rounded-full bg-[#EDF5FF] text-2xl font-semibold text-[#3D6FC2] flex items-center justify-center" :foto="pacienteAbierto.foto" :texto="iniciales(pacienteAbierto)" />
              <div class="text-2xl font-semibold text-[#182234] wrap-break-word">{{ nombreCompleto(pacienteAbierto) }}</div>
              <div class="text-xs text-[#61718B]">Paciente desde {{ pacienteDesde(pacienteAbierto) }}</div>
            </div>

            <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

            <div class="flex flex-col gap-1">
              <span class="text-xs text-[#61718B]">Correo electrónico</span>
              <span class="text-sm font-semibold text-[#182234] wrap-break-word">{{ pacienteAbierto.mail }}</span>
            </div>

            <div class="grid grid-cols-2 gap-x-3 gap-y-4">
              <div v-for="dato in datosPaciente" :key="dato.titulo" class="flex flex-col gap-1">
                <span class="text-xs text-[#61718B]">{{ dato.titulo }}</span>
                <span class="text-sm font-semibold text-[#182234]">{{ dato.valor }}</span>
              </div>
            </div>

            <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

            <div class="shrink-0 px-4 py-3 bg-[#EDF5FF] rounded-xl flex flex-col gap-1.5">
              <span class="text-xs font-semibold text-[#3D6FC2]">PRÓXIMO TURNO</span>
              <template v-if="pacienteAbierto.proximoTurno">
                <span class="text-base font-semibold text-[#182234]">{{ formatearTurno(pacienteAbierto.proximoTurno) }}</span>
                <span class="text-xs text-[#61718B] wrap-break-word">{{ especialidadTurno(pacienteAbierto.proximoTurno) }}<template v-if="pacienteAbierto.proximoTurno.notas"> · {{ pacienteAbierto.proximoTurno.notas }}</template></span>
              </template>
              <span v-else class="text-sm text-[#61718B]">Sin turnos próximos</span>
            </div>

            <div class="flex flex-col gap-1.5">
              <span class="text-base font-semibold text-[#182234]">Notas rápidas</span>
              <p class="text-sm text-[#61718B] wrap-break-word">{{ pacienteAbierto.notaRapida || 'Todavía no agregaste notas sobre este paciente.' }}</p>
            </div>
          </section>

          <section class="flex-1 min-w-0 min-h-96 lg:min-h-0 p-6 bg-white rounded-2xl shadow-[0_0.25rem_1rem_0_rgba(26,51,89,0.08)] flex flex-col gap-3.5">
            <div class="shrink-0 flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-[#182234]">Historial de turnos</h2>
                <p class="text-xs text-[#61718B]">{{ fichasPaciente.length }} turno{{ fichasPaciente.length !== 1 ? 's' : '' }} anterior{{ fichasPaciente.length !== 1 ? 'es' : '' }} · Del más reciente al más antiguo</p>
              </div>
              <span class="shrink-0 text-xs font-semibold text-[#3D6FC2]">{{ cantidadFichas }} ficha{{ cantidadFichas !== 1 ? 's' : '' }} médica{{ cantidadFichas !== 1 ? 's' : '' }}</span>
            </div>

            <input v-model="busquedaFichas" type="text" placeholder="Buscar por fecha o contenido de la ficha…" class="shrink-0 h-11 px-4 bg-[#F4F7FB] rounded-lg text-sm text-[#182234] placeholder:text-[#61718B] outline-none" />

            <p v-if="errorDescarga" class="shrink-0 text-xs text-red-600">{{ errorDescarga }}</p>

            <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-3.5">
              <p v-if="!fichasPaciente.length" class="text-sm text-[#61718B]">Todavía no hay turnos anteriores con este paciente.</p>
              <p v-else-if="!fichasFiltradas.length" class="text-sm text-[#61718B]">No encontramos fichas con esa búsqueda.</p>

              <template v-for="{ turno, devolucion } in fichasFiltradas" :key="turno.id_turno">
                <article v-if="devolucion && fichaAbierta === turno.id_turno" class="shrink-0 p-5 bg-[#EDF5FF] rounded-xl flex flex-col gap-3.5">
                  <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0">
                      <button class="text-left text-lg font-semibold text-[#182234] cursor-pointer" @click="fichaAbierta = fichaAbierta === turno.id_turno ? null : turno.id_turno">{{ fechaLarga(turno) }}</button>
                      <div class="text-xs text-[#61718B]">{{ especialidadTurno(turno) }}</div>
                    </div>
                    <span class="shrink-0 text-xs font-semibold text-[#3D6FC2]">{{ tipoFicha(devolucion) }}</span>
                  </div>
                  <div class="h-px bg-[#D7E2F0]"></div>

                  <h3 class="text-base font-semibold text-[#182234]">Evolución de la consulta</h3>
                  <p v-if="devolucion.contenido" class="text-sm text-[#182234] whitespace-pre-line wrap-break-word">{{ devolucion.contenido }}</p>
                  <p v-else class="text-sm text-[#61718B]">No hay ficha escrita para este turno.</p>

                  <div class="flex flex-wrap items-center justify-between gap-3">
                    <span class="text-xs text-[#61718B]">Registrada por {{ nombreUsuario }} · {{ fechaRegistro(devolucion) }}</span>
                    <button v-if="devolucion.archivo_nombre" class="text-sm font-semibold text-[#3D6FC2] cursor-pointer hover:underline" @click="descargarArchivo(devolucion)">Descargar archivo ↓</button>
                  </div>
                </article>

                <div v-else class="shrink-0 min-h-16 px-4 py-3 bg-[#F4F7FB] rounded-[0.625rem] flex items-center justify-between gap-4">
                  <div class="min-w-0">
                    <div class="text-base font-semibold text-[#182234]">{{ formatearTurno(turno) }}</div>
                    <div class="text-xs text-[#61718B] truncate">{{ especialidadTurno(turno) }}<template v-if="devolucion"> · {{ tipoFicha(devolucion) }}</template></div>
                  </div>
                  <button v-if="devolucion" class="shrink-0 text-sm font-semibold text-[#3D6FC2] cursor-pointer hover:underline" @click="fichaAbierta = fichaAbierta === turno.id_turno ? null : turno.id_turno">Abrir ficha ›</button>
                </div>
              </template>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>
