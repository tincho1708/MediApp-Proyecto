<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal-usuario',
  'ir-a-chatbot',
  'ir-a-reservar-turno',
  'ir-a-mi-usuario-paciente',
  'ir-a-notificaciones',
])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const API = import.meta.env.VITE_API_URL
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)
function cerrarAlClickFuera() {
  esta.value = false
}
onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Especialidad = { id_especialidad: number; nombre_especialidad: string }
type Medico = {
  id: number
  nombre: string
  apellido: string
  telefono: string | null
  mail: string
  especialidades: Especialidad[]
}
type Turno = { id_medicos: number; fecha_hora: string; estado: { estado: string } }
type Horario = { dia_semana: number; hora: number }

// ---- Carga de datos ----
const medicos = ref<Medico[]>([])
const especialidades = ref<Especialidad[]>([])
const misTurnos = ref<Turno[]>([])
const cargando = ref(true)
const error = ref('')

async function cargarDatos() {
  try {
    const [resMedicos, resEspecialidades, resTurnos] = await Promise.all([
      fetch(`${API}/medicos`),
      fetch(`${API}/especialidades`),
      fetch(`${API}/turnos/mis-turnos`, { headers: { Authorization: `Bearer ${sesion.token}` } }),
    ])
    if (!resMedicos.ok) throw new Error()
    medicos.value = await resMedicos.json()
    if (resEspecialidades.ok) especialidades.value = await resEspecialidades.json()
    if (resTurnos.ok) misTurnos.value = await resTurnos.json()
  } catch {
    error.value = 'No se pudieron cargar los profesionales. Intentá de nuevo más tarde.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargarDatos)

// ---- Filtros ----
const busqueda = ref('')
const especialidadId = ref<number | null>(null)

function coincide(m: Medico) {
  const texto = busqueda.value.trim().toLowerCase()
  const coincideTexto =
    !texto ||
    `${m.nombre} ${m.apellido}`.toLowerCase().includes(texto) ||
    m.especialidades.some((e) => e.nombre_especialidad.toLowerCase().includes(texto))
  const coincideEspecialidad =
    especialidadId.value === null ||
    m.especialidades.some((e) => e.id_especialidad === especialidadId.value)
  return coincideTexto && coincideEspecialidad
}

// ---- Mis médicos: profesionales con los que el paciente tiene o tuvo un turno ----
// Guarda, por cada médico, si el vínculo es un turno próximo o una turno de antes
const vinculos = computed(() => {
  const ahora = Date.now()
  const mapa = new Map<number, 'Turno próximo' | 'Atención anterior'>()
  for (const t of misTurnos.value) {
    if (!['pendiente', 'aceptado'].includes(t.estado.estado)) continue
    if (new Date(t.fecha_hora).getTime() >= ahora) mapa.set(t.id_medicos, 'Turno próximo')
    else if (!mapa.has(t.id_medicos)) mapa.set(t.id_medicos, 'Atención anterior')
  }
  return mapa
})

const misMedicos = computed(() =>
  medicos.value.filter((m) => vinculos.value.has(m.id) && coincide(m)),
)
const todosFiltrados = computed(() => medicos.value.filter(coincide))

// ---- Perfil ----
const nombresDia = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const perfil = ref<Medico | null>(null)
const horariosPerfil = ref<Horario[]>([])
const cargandoHorarios = ref(false)

async function verPerfil(m: Medico) {
  perfil.value = m
  horariosPerfil.value = []
  cargandoHorarios.value = true
  try {
    const res = await fetch(`${API}/medicos/${m.id}/horarios`)
    if (res.ok) horariosPerfil.value = await res.json()
  } finally {
    cargandoHorarios.value = false
  }
}

const diasAtencion = computed(() => {
  const porDia = new Map<number, number[]>()
  for (const h of horariosPerfil.value) {
    porDia.set(h.dia_semana, [...(porDia.get(h.dia_semana) ?? []), h.hora])
  }
  const pad = (n: number) => `${String(n).padStart(2, '0')}:00`
  return [...porDia.entries()]
    .sort(([a], [b]) => a - b)
    .map(([dia, horas]) => ({
      dia: nombresDia[dia],
      rango: `${pad(Math.min(...horas))} – ${pad(Math.max(...horas) + 1)}`,
    }))
})

function iniciales(m: Medico) {
  return `${m.nombre.charAt(0)}${m.apellido.charAt(0)}`.toUpperCase()
}
function especialidadesTexto(m: Medico) {
  return m.especialidades.map((e) => e.nombre_especialidad).join(', ') || 'Sin especialidad'
}
function solicitarTurno(m: Medico) {
  emit('ir-a-reservar-turno', m.id)
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
        <button class="campoo activo">Profesionales<span class="campoo-indicador"></span></button>
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

          <button @click="emit('ir-a-mi-usuario-paciente')">
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

    <div class="min-h-screen pt-[4.9rem] font-['Inter']">
      <div class="max-w-328 w-full mx-auto px-4 sm:px-8 pt-10 pb-12 flex flex-col gap-6">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Encontrá a tu profesional</h1>
          <p class="text-sm text-slate-500 mt-2">
            Buscá por nombre o especialidad y solicitá tu próximo turno.
          </p>
        </div>

        <!-- Buscador -->
        <div class="tarjeta p-4 sm:px-6 sm:py-7 flex flex-col sm:flex-row gap-3">
          <label class="flex-1 h-11 px-3 bg-slate-50 rounded-xl flex items-center gap-3">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input v-model="busqueda" type="text" placeholder="Buscar por nombre o especialidad" class="w-full bg-transparent text-sm text-slate-900 placeholder:text-slate-500 outline-none" />
          </label>
          <select v-model="especialidadId" class="sm:w-64 h-11 px-4 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer">
            <option :value="null">Todas las especialidades</option>
            <option v-for="e in especialidades" :key="e.id_especialidad" :value="e.id_especialidad">
              {{ e.nombre_especialidad }}
            </option>
          </select>
        </div>

        <p v-if="cargando" class="text-sm text-slate-500">Cargando profesionales...</p>
        <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

        <template v-else>
          <!-- Mis médicos -->
          <section v-if="misMedicos.length" class="flex flex-col gap-4">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Mis médicos</h2>
              <p class="text-xs text-slate-500">
                Profesionales con los que ya tenés un vínculo o un turno próximo.
              </p>
            </div>
            <div class="grilla">
              <div v-for="m in misMedicos" :key="m.id" class="tarjeta p-6 flex flex-col gap-3">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="avatar">{{ iniciales(m) }}</div>
                  <div class="min-w-0">
                    <div class="text-lg font-semibold text-slate-900 truncate">
                      {{ m.nombre }} {{ m.apellido }}
                    </div>
                    <div class="text-xs text-slate-500 truncate">{{ especialidadesTexto(m) }}</div>
                  </div>
                </div>
                <span class="text-xs text-[#3D6FC2]">{{ vinculos.get(m.id) }}</span>
                <div class="acciones">
                  <button class="boton-secundario" @click="verPerfil(m)">Ver perfil</button>
                  <button class="boton-primario" @click="solicitarTurno(m)">Solicitar turno</button>
                </div>
              </div>
            </div>
          </section>

          <!-- Todos los profesionales -->
          <section class="flex flex-col gap-4">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Todos los profesionales</h2>
              <p class="text-xs text-slate-500">Explorá el directorio de MediApp.</p>
            </div>
            <p v-if="!todosFiltrados.length" class="text-sm text-slate-500">
              No encontramos profesionales con esos filtros.
            </p>
            <div v-else class="grilla">
              <div v-for="m in todosFiltrados" :key="m.id" class="tarjeta p-6 flex flex-col gap-3">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="avatar">{{ iniciales(m) }}</div>
                  <div class="min-w-0">
                    <div class="text-lg font-semibold text-slate-900 truncate">
                      {{ m.nombre }} {{ m.apellido }}
                    </div>
                    <div class="text-xs text-slate-500 truncate">{{ especialidadesTexto(m) }}</div>
                  </div>
                </div>
                <span v-if="vinculos.has(m.id)" class="text-xs text-[#3D6FC2]"
                  >También en Mis médicos</span
                >
                <div class="acciones">
                  <button class="boton-secundario" @click="verPerfil(m)">Ver perfil</button>
                  <button class="boton-primario" @click="solicitarTurno(m)">Solicitar turno</button>
                </div>
              </div>
            </div>
          </section>
        </template>
      </div>
    </div>

    <!-- Modal de perfil -->
    <div v-if="perfil" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 font-['Inter']" @click="perfil = null">
      <div class="bg-white rounded-3xl p-6 sm:p-8 w-lg max-w-full max-h-full overflow-y-auto flex flex-col gap-5" @click.stop>
        <div class="flex items-center gap-4">
          <div class="avatar size-14! text-base!">{{ iniciales(perfil) }}</div>
          <div class="min-w-0">
            <div class="text-xl font-semibold text-slate-900 truncate">
              {{ perfil.nombre }} {{ perfil.apellido }}
            </div>
            <div class="text-sm text-slate-500">{{ especialidadesTexto(perfil) }}</div>
          </div>
        </div>

        <div class="p-4 bg-slate-50 rounded-2xl flex flex-col gap-2 text-sm">
          <div>
            <span class="text-slate-400">Email: </span
            ><span class="text-slate-900">{{ perfil.mail }}</span>
          </div>
          <div v-if="perfil.telefono">
            <span class="text-slate-400">Teléfono: </span
            ><span class="text-slate-900">{{ perfil.telefono }}</span>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <span class="text-sm font-semibold text-slate-900">Días de atención</span>
          <p v-if="cargandoHorarios" class="text-sm text-slate-400">Cargando horarios...</p>
          <p v-else-if="!diasAtencion.length" class="text-sm text-slate-400">
            Este profesional todavía no cargó sus horarios.
          </p>
          <div v-else class="flex flex-col gap-1">
            <div v-for="d in diasAtencion" :key="d.dia" class="flex justify-between text-sm">
              <span class="text-slate-500">{{ d.dia }}</span>
              <span class="font-medium text-[#3D6FC2]">{{ d.rango }}</span>
            </div>
          </div>
        </div>

        <div class="acciones">
          <button class="boton-secundario" @click="perfil = null">Cerrar</button>
          <button class="boton-primario" @click="solicitarTurno(perfil)">Solicitar turno</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.tarjeta {
  @apply bg-white rounded-3xl outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)];
}
.grilla {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6;
}
.avatar {
  @apply size-11 shrink-0 rounded-full bg-blue-50 text-[#3D6FC2] text-sm font-medium flex items-center justify-center;
}
.acciones {
  @apply mt-auto pt-2 flex gap-3;
}
.boton-secundario {
  @apply flex-2 h-10 bg-white rounded-xl outline-1 -outline-offset-1 outline-slate-200 text-sm font-medium text-[#3D6FC2] cursor-pointer hover:bg-slate-50 transition-colors;
}
.boton-primario {
  @apply flex-3 h-10 bg-[#3D6FC2] rounded-xl text-sm font-medium text-white cursor-pointer hover:opacity-90 transition-opacity;
}
</style>
