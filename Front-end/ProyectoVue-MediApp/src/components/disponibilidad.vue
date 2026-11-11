<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-chatbot',
  'ir-a-calendario',
  'ir-a-MediPlus',
  'ir-a-solicitudes',
  'ir-a-reservar-turno',
  'ir-a-mis-pacientes',
  'ir-a-configuracion',
  'ir-a-mi-usuario',
  'ir-a-seguridad',
])
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

function token() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  return sesion.token as string | undefined
}

const DIAS = [
  { dia: 0, nombre: 'Lunes' },
  { dia: 1, nombre: 'Martes' },
  { dia: 2, nombre: 'Miércoles' },
  { dia: 3, nombre: 'Jueves' },
  { dia: 4, nombre: 'Viernes' },
  { dia: 5, nombre: 'Sábado' },
  { dia: 6, nombre: 'Domingo' },
]
const HORAS = Array.from({ length: 24 }, (_, h) => h)
const DURACIONES = [15, 20, 30, 45, 60]
const MARGENES = [0, 5, 10, 15]
const CAMPOS = [
  { clave: 'desde', texto: 'Desde' },
  { clave: 'hasta', texto: 'hasta' },
] as const

type DiaConfig = { activo: boolean; desde: number; hasta: number }
type Pausa = { dia: number; desde: number; hasta: number }

function estadoPorDefecto(): Record<number, DiaConfig> {
  const base: Record<number, DiaConfig> = {}
  for (const d of DIAS) base[d.dia] = { activo: false, desde: 9, hasta: 19 }
  return base
}

const horarios = ref<Record<number, DiaConfig>>(estadoPorDefecto())
const pausas = ref<Pausa[]>([])
const duracion = ref(60)
const margen = ref(0)
const fechasBloqueadas = ref<string[]>([])
const nuevaFecha = ref('')

const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const exito = ref('')

const hoyTexto = new Date().toLocaleDateString('sv-SE')

function formatearHora(h: number) {
  return `${String(h).padStart(2, '0')}:00`
}
function textoMargen(minutos: number) {
  return minutos ? `${minutos} minutos` : 'Sin margen'
}
function formatearFecha(fecha: string) {
  return fecha.split('-').reverse().join('/')
}
function nombreDia(dia: number) {
  return DIAS[dia].nombre.toLowerCase()
}

async function cargarHorarios() {
  cargando.value = true
  error.value = ''
  try {
    const headers = { Authorization: `Bearer ${token()}` }
    const [resHorarios, resConfig] = await Promise.all([
      fetch(`${import.meta.env.VITE_API_URL}/medicos/mis-horarios`, { headers }),
      fetch(`${import.meta.env.VITE_API_URL}/medicos/mi-configuracion`, { headers }),
    ])
    if (!resHorarios.ok || !resConfig.ok) throw new Error()
    const data: { dia_semana: number; hora: number }[] = await resHorarios.json()
    const config = await resConfig.json()

    const nuevo = estadoPorDefecto()
    const nuevasPausas: Pausa[] = []
    for (const d of DIAS) {
      const horas = data.filter((h) => h.dia_semana === d.dia).map((h) => h.hora).sort((a, b) => a - b)
      if (!horas.length) continue
      nuevo[d.dia] = { activo: true, desde: horas[0], hasta: horas[horas.length - 1] + 1 }
      for (let i = 0; i < horas.length - 1; i++) {
        if (horas[i + 1] - horas[i] > 1) nuevasPausas.push({ dia: d.dia, desde: horas[i] + 1, hasta: horas[i + 1] })
      }
    }
    horarios.value = nuevo
    pausas.value = nuevasPausas
    duracion.value = config.duracion_turno
    margen.value = config.margen_turno
    fechasBloqueadas.value = config.fechas_bloqueadas
  } catch {
    error.value = 'No se pudieron cargar tus horarios. Intentá de nuevo más tarde.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargarHorarios)

function agregarPausa() {
  const primerDiaActivo = DIAS.find((d) => horarios.value[d.dia].activo)?.dia ?? 0
  pausas.value.push({ dia: primerDiaActivo, desde: 13, hasta: 14 })
}

function quitarPausa(indice: number) {
  pausas.value.splice(indice, 1)
}

function bloquearFecha() {
  if (!nuevaFecha.value || fechasBloqueadas.value.includes(nuevaFecha.value)) return
  fechasBloqueadas.value = [...fechasBloqueadas.value, nuevaFecha.value].sort()
  nuevaFecha.value = ''
}

function quitarFecha(fecha: string) {
  fechasBloqueadas.value = fechasBloqueadas.value.filter((f) => f !== fecha)
}

function validar() {
  const diaInvalido = DIAS.find((d) => horarios.value[d.dia].activo && horarios.value[d.dia].hasta <= horarios.value[d.dia].desde)
  if (diaInvalido) return `El horario de fin del ${nombreDia(diaInvalido.dia)} tiene que ser posterior al de inicio.`

  for (const p of pausas.value) {
    const dia = horarios.value[p.dia]
    if (!dia.activo) return `Hay una pausa el ${nombreDia(p.dia)}, pero ese día no atendés.`
    if (p.hasta <= p.desde) return `La pausa del ${nombreDia(p.dia)} tiene que terminar después de empezar.`
    if (p.desde < dia.desde || p.hasta > dia.hasta) return `La pausa del ${nombreDia(p.dia)} tiene que estar dentro de tu horario.`
  }
  return ''
}

function horasDeAtencion() {
  const lista: { dia_semana: number; hora: number }[] = []
  for (const d of DIAS) {
    const cfg = horarios.value[d.dia]
    if (!cfg.activo) continue
    for (let h = cfg.desde; h < cfg.hasta; h++) {
      const enPausa = pausas.value.some((p) => p.dia === d.dia && h >= p.desde && h < p.hasta)
      if (!enPausa) lista.push({ dia_semana: d.dia, hora: h })
    }
  }
  return lista
}

async function guardar(url: string, datos: object) {
  const res = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
    body: JSON.stringify(datos),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'No se pudieron guardar los cambios.')
}

async function guardarCambios() {
  exito.value = ''
  error.value = validar()
  if (error.value) return

  guardando.value = true
  try {
    await guardar('/medicos/mis-horarios', { horarios: horasDeAtencion() })
    await guardar('/medicos/mi-configuracion', {
      duracion_turno: duracion.value,
      margen_turno: margen.value,
      fechas_bloqueadas: fechasBloqueadas.value,
    })
    exito.value = 'Disponibilidad guardada correctamente.'
  } catch (e) {
    error.value = e instanceof Error && e.message !== 'Failed to fetch' ? e.message : 'No se pudo conectar al servidor.'
  } finally {
    guardando.value = false
  }
}

function cancelarCambios() {
  exito.value = ''
  error.value = ''
  cargarHorarios()
}
</script>

<template>
  <div class="navbar">
    <button @click="emit('ir-a-principal')">
      <div class="navbar-logo" style="cursor: pointer">
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


        <button @click="emit('ir-a-mi-usuario')">
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
    <div class="flex-1 min-h-0 px-4 sm:px-16 pt-6 pb-6 flex flex-col gap-5">
      <div class="shrink-0">
        <h1 class="text-3xl font-semibold text-[#182234]">Configuración</h1>
        <p class="text-sm text-[#61718B] mt-1">Administrá tu cuenta y la disponibilidad de tu consultorio.</p>
      </div>

      <div class="lg:flex-1 lg:min-h-0 flex flex-col lg:flex-row gap-6">
        <nav class="lg:w-60 shrink-0 p-5 bg-white rounded-2xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11)] flex flex-col gap-2 text-sm text-[#182234]">
          <button class="h-12 px-3 rounded-xl flex items-center gap-3 text-left cursor-pointer hover:bg-[#F4F7FB]" @click="emit('ir-a-mi-usuario')">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></svg>
            Mi usuario
          </button>
          <button class="h-12 px-3 rounded-xl flex items-center gap-3 text-left cursor-pointer hover:bg-[#F4F7FB]" @click="emit('ir-a-seguridad')">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" /></svg>
            Seguridad
          </button>
          <div class="h-12 px-3 rounded-xl flex items-center gap-3">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
            Preferencias
          </div>
          <div class="h-12 px-3 rounded-xl flex items-center gap-3 bg-[#EDF5FF] font-semibold text-[#3D6FC2]">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
            Disponibilidad
          </div>

          <div class="mt-auto pt-2 border-t border-[#D7E2F0]">
            <button class="w-full h-11 px-3 flex items-center gap-3 text-[#BE185D] cursor-pointer" @click="emit('ir-a-bienvenida')">
              <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
              Cerrar sesión
            </button>
          </div>
        </nav>

        <section class="flex-1 min-w-0 min-h-0 p-6 bg-white rounded-2xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11)] flex flex-col gap-4">
          <div class="shrink-0">
            <h2 class="text-2xl font-semibold text-[#182234]">Disponibilidad</h2>
            <p class="text-sm text-[#61718B] mt-1">Definí cuándo pueden reservar turnos tus pacientes.</p>
          </div>
          <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

          <p v-if="cargando" class="text-sm text-[#61718B]">Cargando tus horarios...</p>

          <div v-else class="lg:flex-1 lg:min-h-0 lg:overflow-y-auto flex flex-col xl:flex-row gap-6">
            <div class="flex-1 min-w-0 flex flex-col gap-3">
              <div>
                <h3 class="text-lg font-semibold text-[#182234]">Horario semanal</h3>
                <p class="text-sm text-[#61718B] mt-1">Activá tus días de atención y elegí el horario de inicio y fin.</p>
              </div>

              <div class="flex flex-col gap-1.5">
                <div v-for="d in DIAS" :key="d.dia" class="min-h-10 flex flex-wrap items-center gap-3">
                  <span class="w-24 text-sm font-medium text-[#182234]">{{ d.nombre }}</span>
                  <label class="relative inline-flex items-center cursor-pointer shrink-0">
                    <input v-model="horarios[d.dia].activo" type="checkbox" class="sr-only peer" />
                    <span class="w-10 h-6 bg-[#D7E2F0] peer-checked:bg-[#3D6FC2] rounded-full transition-colors"></span>
                    <span class="absolute left-1 size-4 bg-white rounded-full transition-transform peer-checked:translate-x-4"></span>
                  </label>

                  <div v-if="horarios[d.dia].activo" class="flex flex-wrap items-center gap-2">
                    <template v-for="campo in CAMPOS" :key="campo.clave">
                      <span class="text-xs text-[#61718B]">{{ campo.texto }}</span>
                      <div class="relative">
                        <select v-model.number="horarios[d.dia][campo.clave]" class="w-32 h-9 pl-3 pr-8 bg-[#F4F7FB] rounded-xl outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234] appearance-none cursor-pointer">
                          <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
                        </select>
                        <svg style="width: 1rem; height: 1rem" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                      </div>
                    </template>
                  </div>
                  <span v-else class="text-sm text-[#61718B]">Sin atención</span>
                </div>
              </div>
            </div>

            <aside class="xl:w-96 xl:self-start shrink-0 p-5 bg-[#F4F7FB] rounded-xl flex flex-col gap-4">
              <h3 class="text-lg font-semibold text-[#182234]">Ajustes de los turnos</h3>
              <label class="flex flex-col gap-2">
                <span class="text-sm font-semibold text-[#182234]">Duración de cada turno</span>
                <div class="relative">
                  <select v-model.number="duracion" class="w-full h-11 pl-3 pr-8 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234] appearance-none cursor-pointer">
                    <option v-for="m in DURACIONES" :key="m" :value="m">{{ m }} minutos</option>
                  </select>
                  <svg style="width: 1rem; height: 1rem" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                </div>
              </label>
              <label class="flex flex-col gap-2">
                <span class="text-sm font-semibold text-[#182234]">Tiempo entre turnos</span>
                <div class="relative">
                  <select v-model.number="margen" class="w-full h-11 pl-3 pr-8 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234] appearance-none cursor-pointer">
                    <option v-for="m in MARGENES" :key="m" :value="m">{{ textoMargen(m) }}</option>
                  </select>
                  <svg style="width: 1rem; height: 1rem" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                </div>
              </label>
              <div class="h-px bg-[#D7E2F0]"></div>
              <div>
                <h3 class="text-lg font-semibold text-[#182234]">Pausas y excepciones</h3>
                <p class="text-sm text-[#61718B] mt-1">Reservá un descanso o indicá una fecha en la que no vas a atender.</p>
              </div>

              <div v-for="(pausa, i) in pausas" :key="i" class="flex flex-wrap items-center gap-2 text-sm">
                <select v-model.number="pausa.dia" class="h-9 px-2 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-[#182234] cursor-pointer">
                  <option v-for="d in DIAS" :key="d.dia" :value="d.dia">{{ d.nombre }}</option>
                </select>
                <select v-model.number="pausa.desde" class="h-9 px-2 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-[#182234] cursor-pointer">
                  <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
                </select>
                <span class="text-xs text-[#61718B]">a</span>
                <select v-model.number="pausa.hasta" class="h-9 px-2 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-[#182234] cursor-pointer">
                  <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
                </select>
                <button class="ml-auto text-xs font-medium text-[#BE185D] cursor-pointer hover:underline" @click="quitarPausa(i)">Quitar</button>
              </div>
              <button class="h-11 px-4 bg-white rounded-xl outline-1 -outline-offset-1 outline-[#D7E2F0] text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="agregarPausa">Agregar pausa</button>

              <div class="flex flex-col sm:flex-row gap-3">
                <input v-model="nuevaFecha" type="date" :min="hoyTexto" class="flex-1 min-w-0 h-11 px-3 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234]" />
                <button class="shrink-0 h-11 px-4 bg-white rounded-xl outline-1 -outline-offset-1 outline-[#D7E2F0] text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors disabled:opacity-50 disabled:cursor-not-allowed" :disabled="!nuevaFecha" @click="bloquearFecha">Bloquear fecha</button>
              </div>
              <div v-if="fechasBloqueadas.length" class="flex flex-wrap gap-2">
                <span v-for="f in fechasBloqueadas" :key="f" class="h-8 pl-3 pr-2 bg-white rounded-lg outline-1 -outline-offset-1 outline-[#D7E2F0] flex items-center gap-2 text-sm text-[#182234]">
                  {{ formatearFecha(f) }}
                  <button class="text-[#61718B] cursor-pointer hover:text-[#BE185D]" :aria-label="`Desbloquear ${formatearFecha(f)}`" @click="quitarFecha(f)">✕</button>
                </span>
              </div>

              <p v-if="!pausas.length && !fechasBloqueadas.length" class="pt-1 text-xs text-[#61718B]">Sin pausas ni fechas bloqueadas.</p>
            </aside>
          </div>

          <div class="shrink-0 mt-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span class="text-xs" :class="error ? 'text-red-600' : exito ? 'text-green-600' : 'text-[#61718B]'">{{ error || exito || 'Los cambios se aplican al guardar.' }}</span>
            <div class="flex gap-3">
              <button class="w-32 h-11 px-4 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="cancelarCambios">Cancelar</button>
              <button class="w-52 h-11 px-4 bg-[#3D6FC2] rounded-xl text-base font-medium text-white cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-50" :disabled="guardando || cargando" @click="guardarCambios">{{ guardando ? 'Guardando...' : 'Guardar cambios' }}</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
