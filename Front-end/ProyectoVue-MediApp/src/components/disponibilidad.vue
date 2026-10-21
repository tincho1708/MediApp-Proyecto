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
  { dia: 2, nombre: 'Miercoles' },
  { dia: 3, nombre: 'Jueves' },
  { dia: 4, nombre: 'Viernes' },
  { dia: 5, nombre: 'Sabado' },
  { dia: 6, nombre: 'Domingo' },
]

type DiaConfig = { activo: boolean; desde: number; hasta: number }

function estadoPorDefecto(): Record<number, DiaConfig> {
  const base: Record<number, DiaConfig> = {}
  for (const d of DIAS) base[d.dia] = { activo: false, desde: 9, hasta: 19 }
  return base
}

const horarios = ref<Record<number, DiaConfig>>(estadoPorDefecto())
const todos = ref<DiaConfig>({ activo: false, desde: 9, hasta: 19 })

const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const exito = ref('')

const HORAS = Array.from({ length: 24 }, (_, h) => h)
function formatearHora(h: number) {
  return `${String(h).padStart(2, '0')}:00`
}

async function cargarHorarios() {
  cargando.value = true
  error.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos/mis-horarios`, {
      headers: { Authorization: `Bearer ${token()}` },
    })
    if (!res.ok) throw new Error()
    const data: { dia_semana: number; hora: number }[] = await res.json()

    const nuevo = estadoPorDefecto()
    for (const d of DIAS) {
      const horas = data.filter((h) => h.dia_semana === d.dia).map((h) => h.hora)
      if (horas.length) {
        nuevo[d.dia] = { activo: true, desde: Math.min(...horas), hasta: Math.max(...horas) + 1 }
      }
    }
    horarios.value = nuevo
  } catch {
    error.value = 'No se pudieron cargar tus horarios. Intentá de nuevo más tarde.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargarHorarios)

function aplicarATodos() {
  const nuevo = estadoPorDefecto()
  for (const d of DIAS) {
    nuevo[d.dia] = { ...todos.value }
  }
  horarios.value = nuevo
}

async function guardarCambios() {
  guardando.value = true
  error.value = ''
  exito.value = ''
  const lista: { dia_semana: number; hora: number }[] = []
  for (const d of DIAS) {
    const cfg = horarios.value[d.dia]
    if (!cfg.activo) continue
    for (let h = cfg.desde; h < cfg.hasta; h++) {
      lista.push({ dia_semana: d.dia, hora: h })
    }
  }

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos/mis-horarios`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify({ horarios: lista }),
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.detail || 'No se pudieron guardar los cambios.'
      return
    }
    exito.value = 'Horarios guardados correctamente.'
  } catch {
    error.value = 'No se pudo conectar al servidor.'
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

  <div class="titulo-pagina w-fit text-zinc-900 text-4xl font-semibold font-['Inter'] pb-2 mb-6 border-b-2 border-black">
    Configuracion
  </div>

  <div class="contenido-pagina flex gap-6 items-start font-['Inter']">
    <div class="w-64 h-[32.5rem] bg-white rounded-2xl border border-sky-500 shadow-[0rem_0.25rem_1.25rem_0.125rem_rgba(0,0,0,0.15)] p-5 flex flex-col gap-1 shrink-0">
      <button class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70 hover:bg-sky-50 text-left" @click="emit('ir-a-mi-usuario')">
        <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
        </svg>
        Mi usuario
      </button>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        Notificaciones
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
        </svg>
        Seguridad
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.04-1.56V3a2 2 0 0 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 0 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15Z" />
        </svg>
        Configuracion
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl bg-sky-500 text-white font-medium">
        <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <rect x="3" y="4" width="18" height="18" rx="2" />
          <path d="M16 2v4M8 2v4M3 10h18" />
        </svg>
        Disponibilidad
      </div>

      <div class="flex-1"></div>
      <hr class="border-zinc-200 my-2" />
      <button class="flex items-center gap-3 px-3 py-3 rounded-xl bg-red-100 text-red-500 font-medium" @click="emit('ir-a-bienvenida')">
        <svg style="width: 1.125rem; height: 1.125rem" cursor="pointer" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        Cerrar sesion
      </button>
    </div>

    <div class="flex-1 bg-white rounded-2xl border border-sky-500 shadow-[0rem_0.25rem_1.25rem_0.125rem_rgba(0,0,0,0.15)] p-8">
      <h1 class="text-2xl font-semibold">Disponibilidad</h1>
      <p class="text-black/50 mt-1">Definí tus horarios de atención durante la semana</p>

      <p v-if="cargando" class="text-black mt-6">Cargando tus horarios...</p>

      <template v-else>
        <div class="mt-8 text-sm font-semibold tracking-wide text-black/50">HORARIO SEMANAL</div>

        <div class="mt-3 flex items-center gap-4 py-2">
          <span class="w-24 font-semibold">TODOS</span>
          <label class="relative inline-flex items-center cursor-pointer shrink-0">
            <input type="checkbox" v-model="todos.activo" class="sr-only peer" @change="aplicarATodos" />
            <div class="w-11 h-6 bg-zinc-300 peer-checked:bg-sky-500 rounded-full transition-colors"></div>
            <div class="absolute left-1 top-1 bg-white size-4 rounded-full transition-transform peer-checked:translate-x-5"></div>
          </label>
          <select v-model.number="todos.desde" class="border border-zinc-300 rounded-lg px-3 py-1.5" @change="aplicarATodos">
            <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
          </select>
          <span>a</span>
          <select v-model.number="todos.hasta" class="border border-zinc-300 rounded-lg px-3 py-1.5" @change="aplicarATodos">
            <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
          </select>
        </div>
        <hr class="border-zinc-200" />

        <template v-for="d in DIAS" :key="d.dia">
          <div class="flex items-center gap-4 py-3">
            <span class="w-24">{{ d.nombre }}</span>
            <label class="relative inline-flex items-center cursor-pointer shrink-0">
              <input type="checkbox" v-model="horarios[d.dia].activo" class="sr-only peer" />
              <div class="w-11 h-6 bg-zinc-300 peer-checked:bg-sky-500 rounded-full transition-colors"></div>
              <div class="absolute left-1 top-1 bg-white size-4 rounded-full transition-transform peer-checked:translate-x-5"></div>
            </label>
            <select v-model.number="horarios[d.dia].desde" class="border border-zinc-300 rounded-lg px-3 py-1.5" :disabled="!horarios[d.dia].activo">
              <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
            </select>
            <span>a</span>
            <select v-model.number="horarios[d.dia].hasta" class="border border-zinc-300 rounded-lg px-3 py-1.5" :disabled="!horarios[d.dia].activo">
              <option v-for="h in HORAS" :key="h" :value="h">{{ formatearHora(h) }}</option>
            </select>
          </div>
          <hr class="border-zinc-100" />
        </template>

        <p v-if="error" class="text-red-500 mt-4">{{ error }}</p>
        <p v-if="exito" class="text-green-600 mt-4">{{ exito }}</p>

        <div class="flex justify-end gap-3 mt-6">
          <button class="px-5 py-2.5 rounded-xl bg-zinc-200 font-medium hover:bg-zinc-300" @click="cancelarCambios">
            Cancelar
          </button>
          <button class="px-5 py-2.5 rounded-xl bg-sky-500 text-white font-medium hover:bg-sky-600 disabled:opacity-50" :disabled="guardando" @click="guardarCambios">
            {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.titulo-pagina {
  margin-top: 7.5rem;
  margin-left: 2.5rem;
}

.contenido-pagina {
  margin-left: 2.5rem;
  margin-right: 2.5rem;
}
</style>
