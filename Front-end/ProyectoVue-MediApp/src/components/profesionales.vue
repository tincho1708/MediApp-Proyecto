<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
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
  duracion_turno: number
  edad: number | null
  foto: string | null
}
type Turno = {
  id_turno: number
  id_medicos: number
  fecha_hora: string
  estado: { estado: string }
  especialidad?: Especialidad | null
}
type Devolucion = {
  id: number
  id_turno: number | null
  contenido: string | null
  archivo_nombre: string | null
  fecha: string
}

// ---- Carga de datos ----
const medicos = ref<Medico[]>([])
const especialidades = ref<Especialidad[]>([])
const misTurnos = ref<Turno[]>([])
const misDevoluciones = ref<Devolucion[]>([])
const cargando = ref(true)
const error = ref('')

async function cargarDatos() {
  const headers = { Authorization: `Bearer ${sesion.token}` }
  try {
    const [resMedicos, resEspecialidades, resTurnos, resDevoluciones] = await Promise.all([
      fetch(`${API}/medicos`),
      fetch(`${API}/especialidades`),
      fetch(`${API}/turnos/mis-turnos`, { headers }),
      fetch(`${API}/devoluciones/mis-devoluciones`, { headers }),
    ])
    if (!resMedicos.ok) throw new Error()
    medicos.value = await resMedicos.json()
    if (resEspecialidades.ok) especialidades.value = await resEspecialidades.json()
    if (resTurnos.ok) misTurnos.value = await resTurnos.json()
    if (resDevoluciones.ok) misDevoluciones.value = await resDevoluciones.json()
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

const POR_PAGINA_MIS_MEDICOS = 4
const POR_PAGINA_DIRECTORIO = 12

const paginaMisMedicos = ref(1)
const paginaDirectorio = ref(1)

const totalPaginasMisMedicos = computed(() => Math.ceil(misMedicos.value.length / POR_PAGINA_MIS_MEDICOS))
const totalPaginasDirectorio = computed(() => Math.ceil(todosFiltrados.value.length / POR_PAGINA_DIRECTORIO))

const misMedicosPagina = computed(() => {
  const inicio = (paginaMisMedicos.value - 1) * POR_PAGINA_MIS_MEDICOS
  return misMedicos.value.slice(inicio, inicio + POR_PAGINA_MIS_MEDICOS)
})
const directorioPagina = computed(() => {
  const inicio = (paginaDirectorio.value - 1) * POR_PAGINA_DIRECTORIO
  return todosFiltrados.value.slice(inicio, inicio + POR_PAGINA_DIRECTORIO)
})

const primeroDirectorio = computed(() => (paginaDirectorio.value - 1) * POR_PAGINA_DIRECTORIO + 1)
const ultimoDirectorio = computed(() => primeroDirectorio.value + directorioPagina.value.length - 1)

watch([busqueda, especialidadId], () => {
  paginaMisMedicos.value = 1
  paginaDirectorio.value = 1
})

// ---- Perfil ----
const perfil = ref<Medico | null>(null)

function verPerfil(m: Medico) {
  perfil.value = m
  busquedaFichas.value = ''
  errorDescarga.value = ''
  fichaAbierta.value = null
}

function iniciales(m: Medico) {
  return `${m.nombre.charAt(0)}${m.apellido.charAt(0)}`.toUpperCase()
}
function especialidadesTexto(m: Medico) {
  return m.especialidades.map((e) => e.nombre_especialidad).join(', ') || 'Sin especialidad'
}
const datosPerfil = computed(() => [
  { titulo: 'Edad', valor: perfil.value?.edad ? `${perfil.value.edad} años` : 'No informada' },
  { titulo: 'Duración del turno', valor: `${perfil.value?.duracion_turno ?? 60} min` },
  { titulo: 'Teléfono', valor: perfil.value?.telefono || 'No informado' },
  { titulo: 'Modalidad', valor: 'Presencial' },
])

function solicitarTurno(m: Medico) {
  emit('ir-a-reservar-turno', m.id)
}

// ---- Pop up: turnos y fichas del médico ----
const nombresMes = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

const busquedaFichas = ref('')
const fichaAbierta = ref<number | null>(null)
const errorDescarga = ref('')

const dosDigitos = (n: number) => String(n).padStart(2, '0')

function fechaNumerica(fecha: Date) {
  return `${dosDigitos(fecha.getDate())}/${dosDigitos(fecha.getMonth() + 1)}/${fecha.getFullYear()}`
}
function fechaLarga(fecha: Date) {
  return `${fecha.getDate()} de ${nombresMes[fecha.getMonth()]} de ${fecha.getFullYear()}`
}
function hora(fecha: Date) {
  return `${dosDigitos(fecha.getHours())}:${dosDigitos(fecha.getMinutes())}`
}
function nombreEspecialidad(t: Turno) {
  return t.especialidad?.nombre_especialidad ?? (perfil.value ? especialidadesTexto(perfil.value) : '')
}
function fechaCompartida(d: Devolucion) {
  return fechaNumerica(new Date(`${d.fecha}Z`))
}
function tipoFicha(d: Devolucion) {
  if (d.contenido && d.archivo_nombre) return 'Ficha escrita y archivo'
  return d.archivo_nombre ? 'Ficha adjunta' : 'Ficha escrita'
}

const turnosDelPerfil = computed(() => misTurnos.value.filter((t) => t.id_medicos === perfil.value?.id && t.estado.estado === 'aceptado'))

const fichasPerfil = computed(() =>
  turnosDelPerfil.value
    .filter((t) => new Date(t.fecha_hora).getTime() < Date.now())
    .sort((a, b) => new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime())
    .map((turno) => ({
      turno,
      fecha: new Date(turno.fecha_hora),
      devolucion: misDevoluciones.value.find((d) => d.id_turno === turno.id_turno) ?? null,
    })),
)

const fichasFiltradas = computed(() => {
  const texto = busquedaFichas.value.trim().toLowerCase()
  if (!texto) return fichasPerfil.value
  return fichasPerfil.value.filter(({ turno, fecha, devolucion }) =>
    [fechaNumerica(fecha), fechaLarga(fecha), nombreEspecialidad(turno), devolucion?.contenido ?? '', devolucion?.archivo_nombre ?? '']
      .some((valor) => valor.toLowerCase().includes(texto)),
  )
})

const cantidadFichas = computed(() => fichasPerfil.value.filter((f) => f.devolucion).length)

const proximoTurno = computed(() => {
  const proximos = turnosDelPerfil.value
    .filter((t) => new Date(t.fecha_hora).getTime() >= Date.now())
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
  return proximos[0] ?? null
})

function alternarFicha(idTurno: number) {
  fichaAbierta.value = fichaAbierta.value === idTurno ? null : idTurno
}

async function descargarArchivo(d: Devolucion) {
  errorDescarga.value = ''
  try {
    const res = await fetch(`${API}/devoluciones/${d.id}/archivo`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) throw new Error()

    const url = URL.createObjectURL(await res.blob())
    const enlace = document.createElement('a')
    enlace.href = url
    enlace.download = d.archivo_nombre ?? 'ficha'
    enlace.click()
    URL.revokeObjectURL(url)
  } catch {
    errorDescarga.value = 'No se pudo descargar el archivo. Intentá de nuevo.'
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

    <div v-show="!perfil" class="min-h-screen pt-[4.9rem] font-['Inter']">
      <div class="w-full px-4 sm:px-16 pt-10 pb-10 flex flex-col gap-5">
        <div>
          <h1 class="text-3xl font-semibold text-[#182234]">Profesionales</h1>
          <p class="text-sm text-[#61718B] mt-1">Tus médicos y nuevas opciones de atención, en un mismo lugar.</p>
        </div>

        <p v-if="cargando" class="text-sm text-[#61718B]">Cargando profesionales...</p>
        <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

        <template v-else>
          <section v-if="misMedicos.length" class="px-6 py-5 bg-[#EDF5FF] rounded-2xl outline-1 -outline-offset-1 outline-[#D7E2F0] flex flex-col gap-4">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-[#3D6FC2]">Mis médicos</h2>
                <p class="text-xs text-[#61718B]">Accedé a su información y a las fichas que compartieron con vos.</p>
              </div>
              <div class="shrink-0 flex items-center gap-4">
                <span class="text-sm font-semibold text-[#3D6FC2]">{{ misMedicos.length }} médico{{ misMedicos.length !== 1 ? 's' : '' }}</span>
                <template v-if="totalPaginasMisMedicos > 1">
                  <button class="boton-pagina" :disabled="paginaMisMedicos === 1" @click="paginaMisMedicos--">‹ Anterior</button>
                  <button class="boton-pagina" :disabled="paginaMisMedicos === totalPaginasMisMedicos" @click="paginaMisMedicos++">Siguiente ›</button>
                </template>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-4 gap-y-3">
              <button v-for="m in misMedicosPagina" :key="m.id" class="tarjeta-medico" @click="verPerfil(m)">
                <Avatar class="avatar-medico" :foto="m.foto" :texto="iniciales(m)" />
                <span class="flex-1 min-w-0 flex flex-col gap-0.5">
                  <span class="text-sm font-semibold text-[#182234] truncate">{{ m.nombre }} {{ m.apellido }}</span>
                  <span class="text-xs text-[#61718B] truncate">{{ especialidadesTexto(m) }}</span>
                </span>
                <span class="shrink-0 text-xl text-[#3D6FC2]">›</span>
              </button>
            </div>
          </section>

          <section class="p-6 bg-white rounded-2xl shadow-[0_0.25rem_1rem_0_rgba(26,51,89,0.08)] flex flex-col gap-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-[#182234]">Encontrá nuevos profesionales</h2>
                <p class="text-xs text-[#61718B]">Explorá el directorio y elegí con quién atenderte.</p>
              </div>
              <span class="shrink-0 text-xs text-[#61718B]">{{ todosFiltrados.length }} profesional{{ todosFiltrados.length !== 1 ? 'es' : '' }}</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-[1fr_18rem] gap-3">
              <label class="h-11 px-4 bg-[#F4F7FB] rounded-lg flex items-center gap-2.5">
                <svg style="width: 1.25rem; height: 1.25rem" class="text-[#61718B] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <circle cx="11" cy="11" r="7" />
                  <path d="m20 20-3.5-3.5" />
                </svg>
                <input v-model="busqueda" type="text" placeholder="Buscar por nombre o especialidad…" class="w-full bg-transparent text-sm text-[#182234] placeholder:text-[#61718B] outline-none" />
              </label>
              <select v-model="especialidadId" class="filtro cursor-pointer">
                <option :value="null">Especialidad</option>
                <option v-for="e in especialidades" :key="e.id_especialidad" :value="e.id_especialidad">
                  {{ e.nombre_especialidad }}
                </option>
              </select>
            </div>

            <p v-if="!todosFiltrados.length" class="text-sm text-[#61718B]">No encontramos profesionales con esos filtros.</p>

            <template v-else>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-4 gap-y-3">
                <button v-for="m in directorioPagina" :key="m.id" class="tarjeta-medico" @click="verPerfil(m)">
                  <Avatar class="avatar-medico" :foto="m.foto" :texto="iniciales(m)" />
                  <span class="flex-1 min-w-0 flex flex-col gap-0.5">
                    <span class="text-sm font-semibold text-[#182234] truncate">{{ m.nombre }} {{ m.apellido }}</span>
                    <span class="text-xs text-[#61718B] truncate">{{ especialidadesTexto(m) }}</span>
                  </span>
                  <span class="shrink-0 text-xl text-[#3D6FC2]">›</span>
                </button>
              </div>

              <div class="flex flex-wrap items-center justify-between gap-3">
                <span class="text-xs text-[#61718B]">Mostrando {{ primeroDirectorio }}–{{ ultimoDirectorio }} de {{ todosFiltrados.length }} profesionales</span>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button class="boton-pagina mr-2" :disabled="paginaDirectorio === 1" @click="paginaDirectorio--">‹ Anterior</button>
                  <button v-for="n in totalPaginasDirectorio" :key="n" class="size-10 rounded-lg flex items-center justify-center cursor-pointer" :class="n === paginaDirectorio ? 'bg-[#3D6FC2] font-semibold text-white' : 'text-[#61718B] hover:bg-[#F4F7FB]'" @click="paginaDirectorio = n">{{ n }}</button>
                  <button class="boton-pagina ml-2" :disabled="paginaDirectorio === totalPaginasDirectorio" @click="paginaDirectorio++">Siguiente ›</button>
                </div>
              </div>
            </template>
          </section>
        </template>
      </div>
    </div>

    <!-- pop up -->
    <div v-if="perfil" class="pop-up-fondo fixed inset-x-0 bottom-0 top-[4.9rem] z-50 overflow-y-auto lg:overflow-hidden font-['Inter']">
      <div class="lg:h-full px-4 sm:px-16 py-6 flex flex-col gap-5">
        <div class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-3xl font-semibold text-[#182234]">Mi profesional y mis fichas</h1>
            <p class="text-sm text-[#61718B] mt-1">Consultá los datos de tu profesional y la información que compartió con vos.</p>
          </div>
          <button class="shrink-0 h-11 px-6 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="perfil = null">← Volver a profesionales</button>
        </div>

        <div class="lg:flex-1 lg:min-h-0 flex flex-col lg:flex-row gap-6">
          <section class="tarjeta-pop-up lg:w-80 shrink-0 p-6 flex flex-col justify-between gap-4 lg:overflow-y-auto">
            <div class="flex flex-col gap-4">
              <Avatar class="size-16 rounded-full bg-[#EDF5FF] text-2xl font-semibold text-[#3D6FC2] flex items-center justify-center" :foto="perfil.foto" :texto="iniciales(perfil)" />
              <div class="text-2xl font-semibold text-[#182234] wrap-break-word">{{ perfil.nombre }} {{ perfil.apellido }}</div>
              <div class="text-base font-semibold text-[#3D6FC2]">{{ especialidadesTexto(perfil) }}</div>
              <div class="text-xs text-[#61718B]">Matrícula nacional · No informada</div>
            </div>

            <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

            <div class="flex flex-col gap-1.5">
              <span class="text-base font-semibold text-[#182234]">Sobre la profesional</span>
              <p class="text-sm text-[#61718B]">Atención en {{ especialidadesTexto(perfil) }} con seguimiento personalizado.</p>
            </div>

            <div class="grid grid-cols-2 gap-x-3 gap-y-4">
              <div v-for="dato in datosPerfil" :key="dato.titulo" class="flex flex-col gap-1 min-w-0">
                <span class="text-xs text-[#61718B]">{{ dato.titulo }}</span>
                <span class="text-sm font-semibold text-[#182234] wrap-break-word">{{ dato.valor }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-1">
              <span class="text-xs text-[#61718B]">Correo electrónico</span>
              <span class="text-sm font-semibold text-[#182234] wrap-break-word">{{ perfil.mail }}</span>
            </div>

            <div v-if="proximoTurno" class="shrink-0 px-4 py-3 bg-[#EDF5FF] rounded-xl flex flex-col gap-1.5">
              <span class="text-xs font-semibold text-[#3D6FC2]">TU PRÓXIMO TURNO</span>
              <span class="text-base font-semibold text-[#182234]">{{ fechaNumerica(new Date(proximoTurno.fecha_hora)) }} · {{ hora(new Date(proximoTurno.fecha_hora)) }}</span>
              <span class="text-xs text-[#61718B]">{{ nombreEspecialidad(proximoTurno) }}</span>
            </div>

            <button class="shrink-0 h-11 bg-[#3D6FC2] rounded-xl text-base font-medium text-white cursor-pointer hover:opacity-90 transition-opacity" @click="solicitarTurno(perfil)">Solicitar nuevo turno</button>
          </section>

          <section class="tarjeta-pop-up flex-1 min-w-0 min-h-96 lg:min-h-0 p-6 flex flex-col gap-3.5">
            <div class="shrink-0 flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-[#182234]">Mis fichas médicas</h2>
                <p class="text-xs text-[#61718B]">Las fichas que {{ perfil.nombre }} {{ perfil.apellido }} compartió con vos.</p>
              </div>
              <span class="shrink-0 text-xs font-semibold text-[#3D6FC2]">{{ cantidadFichas }} ficha{{ cantidadFichas !== 1 ? 's' : '' }}</span>
            </div>

            <input v-model="busquedaFichas" type="text" placeholder="Buscar por fecha o contenido…" class="shrink-0 h-11 px-4 bg-[#F4F7FB] rounded-lg text-sm text-[#182234] placeholder:text-[#61718B] outline-none" />

            <p v-if="errorDescarga" class="shrink-0 text-xs text-red-600">{{ errorDescarga }}</p>

            <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-3.5">
              <p v-if="!fichasPerfil.length" class="text-sm text-[#61718B]">Todavía no tuviste turnos con este profesional.</p>
              <p v-else-if="!fichasFiltradas.length" class="text-sm text-[#61718B]">No encontramos fichas con esa búsqueda.</p>

              <template v-for="{ turno, fecha, devolucion } in fichasFiltradas" :key="turno.id_turno">
                <article v-if="devolucion && fichaAbierta === turno.id_turno" class="shrink-0 p-5 bg-[#EDF5FF] rounded-xl flex flex-col gap-3.5">
                  <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0">
                      <button class="text-left text-lg font-semibold text-[#182234] cursor-pointer" @click="alternarFicha(turno.id_turno)">{{ fechaLarga(fecha) }} · {{ hora(fecha) }}</button>
                      <div class="text-xs text-[#61718B]">{{ nombreEspecialidad(turno) }}</div>
                    </div>
                    <span class="shrink-0 text-xs font-semibold text-[#3D6FC2]">{{ tipoFicha(devolucion) }}</span>
                  </div>
                  <div class="h-px bg-[#D7E2F0]"></div>

                  <h3 class="text-base font-semibold text-[#182234]">Resumen de la consulta</h3>
                  <p v-if="devolucion.contenido" class="text-sm text-[#182234] whitespace-pre-line wrap-break-word">{{ devolucion.contenido }}</p>
                  <p v-else class="text-sm text-[#61718B]">No hay ficha escrita para este turno.</p>

                  <div class="flex flex-wrap items-center justify-between gap-3">
                    <span class="text-xs text-[#61718B]">Compartida por {{ perfil.nombre }} {{ perfil.apellido }} · {{ fechaCompartida(devolucion) }}</span>
                    <button v-if="devolucion.archivo_nombre" class="text-sm font-semibold text-[#3D6FC2] cursor-pointer hover:underline" @click="descargarArchivo(devolucion)">Descargar archivo ↓</button>
                  </div>
                </article>

                <div v-else class="shrink-0 min-h-16 px-4 py-3 bg-[#F4F7FB] rounded-[0.625rem] flex items-center justify-between gap-4">
                  <div class="min-w-0">
                    <div class="text-base font-semibold text-[#182234]">{{ fechaNumerica(fecha) }} · {{ hora(fecha) }}</div>
                    <div class="text-xs text-[#61718B] truncate">{{ nombreEspecialidad(turno) }}<template v-if="devolucion"> · {{ tipoFicha(devolucion) }}</template></div>
                  </div>
                  <button v-if="devolucion" class="shrink-0 text-sm font-semibold text-[#3D6FC2] cursor-pointer hover:underline" @click="alternarFicha(turno.id_turno)">Abrir ficha ›</button>
                </div>
              </template>
            </div>
          </section>
        </div>
      </div>
    </div>

  </div>

</template>

<style scoped>
.tarjeta-medico {
  width: 100%;
  min-width: 0;
  height: 5rem;
  padding: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #ffffff;
  border-radius: 0.75rem;
  outline: 1px solid #d7e2f0;
  outline-offset: -1px;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s ease;
}
.tarjeta-medico:hover {
  background-color: #f4f7fb;
}
.avatar-medico {
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #edf5ff;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #3d6fc2;
}
.boton-pagina {
  font-size: 0.875rem;
  font-weight: 600;
  color: #3d6fc2;
  cursor: pointer;
}
.boton-pagina:hover {
  text-decoration: underline;
}
.boton-pagina:disabled {
  font-weight: 400;
  color: #61718b;
  text-decoration: none;
  cursor: not-allowed;
}
.filtro {
  width: 100%;
  height: 2.75rem;
  padding: 0;
  background-color: #ffffff;
  border-radius: 0.5rem;
  outline: 1px solid #d7e2f0;
  outline-offset: -1px;
  font-size: 0.75rem;
  text-align: center;
  color: #61718b;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2361718B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.875rem;
}
.pop-up-fondo {
  background: linear-gradient(135deg, #bfdbfe 0%, #ffffff 50%, #bfdbfe 100%);
}
.tarjeta-pop-up {
  background-color: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 0.25rem 1rem 0 rgba(26, 51, 89, 0.08);
}
</style>
