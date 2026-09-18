<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-reservar-turno', 'ir-a-mis-pacientes', 'ir-a-configuracion'])
const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

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
      const horas = data.filter(h => h.dia_semana === d.dia).map(h => h.hora)
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
      <div class="navbar-logo" style="cursor:pointer">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
    </button>

    <div class="navbar-acciones">
      <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
      <button class="campoo" @click="emit('ir-a-mis-pacientes')">Mis pacientes</button>
      <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes</button>
      <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+</button>

      <button @click.stop="esta = !esta" class="barra">
        <div class="w-12 h-9 relative">
          <div class="w-12 border-t-2 border-black absolute left-0 top-0"></div>
          <div class="w-12 border-t-2 border-black absolute left-0 top-[1rem]"></div>
          <div class="w-12 border-t-2 border-black absolute left-0 top-[2rem]"></div>
        </div>
      </button>

      <div :class="['barra-desplegable', { 'barra-abierta': esta }]" @click.stop>
        <button href="#">
          <div id="barra-dentro" class="w-50 h-12 rounded-2xl">
            <div class="barra-texto">
              <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 31 32" fill="none">
                <path d="M15.5 0C17.5554 0 19.5267 0.842854 20.9801 2.34315C22.4335 3.84344 23.25 5.87827 23.25 8C23.25 10.1217 22.4335 12.1566 20.9801 13.6569C19.5267 15.1571 17.5554 16 15.5 16C13.4446 16 11.4733 15.1571 10.0199 13.6569C8.56651 12.1566 7.75 10.1217 7.75 8C7.75 5.87827 8.56651 3.84344 10.0199 2.34315C11.4733 0.842854 13.4446 0 15.5 0ZM15.5 4C14.4723 4 13.4867 4.42143 12.76 5.17157C12.0333 5.92172 11.625 6.93913 11.625 8C11.625 9.06087 12.0333 10.0783 12.76 10.8284C13.4867 11.5786 14.4723 12 15.5 12C16.5277 12 17.5133 11.5786 18.24 10.8284C18.9667 10.0783 19.375 9.06087 19.375 8C19.375 6.93913 18.9667 5.92172 18.24 5.17157C17.5133 4.42143 16.5277 4 15.5 4ZM15.5 18C20.6731 18 31 20.66 31 26V32H0V26C0 20.66 10.3269 18 15.5 18ZM15.5 21.8C9.74562 21.8 3.68125 24.72 3.68125 26V28.2H27.3188V26C27.3188 24.72 21.2544 21.8 15.5 21.8Z" fill="black"/>
              </svg>
              Mi cuenta
            </div>
          </div>
        </button>

        <button href="#" @click="emit('ir-a-configuracion')">
          <div id="barra-dentro" class="w-50 h-12 rounded-2xl">
            <div class="barra-texto">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 32 32" fill="none" style="flex-shrink: 0;">
                <path d="M11.6219 32L10.9851 26.88C10.6401 26.7467 10.3154 26.5867 10.0107 26.4C9.70614 26.2133 9.40736 26.0133 9.11443 25.8L4.37811 27.8L0 20.2L4.0995 17.08C4.07297 16.8933 4.0597 16.7136 4.0597 16.5408V15.4608C4.0597 15.2869 4.07297 15.1067 4.0995 14.92L0 11.8L4.37811 4.2L9.11443 6.2C9.4063 5.98667 9.71144 5.78667 10.0299 5.6C10.3483 5.41333 10.6667 5.25333 10.9851 5.12L11.6219 0H20.3781L21.0149 5.12C21.3599 5.25333 21.6852 5.41333 21.9908 5.6C22.2965 5.78667 22.5948 5.98667 22.8856 6.2L27.6219 4.2L32 11.8L27.9005 14.92C27.927 15.1067 27.9403 15.2869 27.9403 15.4608V16.5392C27.9403 16.7131 27.9138 16.8933 27.8607 17.08L31.9602 20.2L27.5821 27.8L22.8856 25.8C22.5937 26.0133 22.2886 26.2133 21.9701 26.4C21.6517 26.5867 21.3333 26.7467 21.0149 26.88L20.3781 32H11.6219ZM14.408 28.8H17.5522L18.1095 24.56C18.932 24.3467 19.6951 24.0336 20.3988 23.6208C21.1025 23.208 21.7457 22.7077 22.3284 22.12L26.2687 23.76L27.8209 21.04L24.398 18.44C24.5307 18.0667 24.6236 17.6736 24.6766 17.2608C24.7297 16.848 24.7562 16.4277 24.7562 16C24.7562 15.5723 24.7297 15.1525 24.6766 14.7408C24.6236 14.3291 24.5307 13.9355 24.398 13.56L27.8209 10.96L26.2687 8.24L22.3284 9.92C21.7446 9.30667 21.1014 8.7936 20.3988 8.3808C19.6962 7.968 18.9331 7.6544 18.1095 7.44L17.592 3.2H14.4478L13.8905 7.44C13.068 7.65333 12.3054 7.96693 11.6028 8.3808C10.9002 8.79467 10.2565 9.2944 9.67164 9.88L5.73134 8.24L4.1791 10.96L7.60199 13.52C7.46932 13.92 7.37645 14.32 7.32338 14.72C7.27032 15.12 7.24378 15.5467 7.24378 16C7.24378 16.4267 7.27032 16.84 7.32338 17.24C7.37645 17.64 7.46932 18.04 7.60199 18.44L4.1791 21.04L5.73134 23.76L9.67164 22.08C10.2554 22.6933 10.8991 23.2069 11.6028 23.6208C12.3065 24.0347 13.0691 24.3477 13.8905 24.56L14.408 28.8ZM16.0796 21.6C17.6186 21.6 18.932 21.0533 20.0199 19.96C21.1078 18.8667 21.6517 17.5467 21.6517 16C21.6517 14.4533 21.1078 13.1333 20.0199 12.04C18.932 10.9467 17.6186 10.4 16.0796 10.4C14.5141 10.4 13.1938 10.9467 12.1186 12.04C11.0435 13.1333 10.5064 14.4533 10.5075 16C10.5085 17.5467 11.0461 18.8667 12.1202 19.96C13.1943 21.0533 14.5141 21.6 16.0796 21.6Z" fill="black"/>
              </svg>
              Configuracion
            </div>
          </div>
        </button>

        <button href="#" style="margin-top: auto;" @click="emit('ir-a-bienvenida')">
          <div class="barra-dentro-cerrar w-50 h-12 rounded-2xl">
            <div class="barra-texto">
              <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 31 32" fill="none" style="flex-shrink: 0;">
                <path d="M3.44444 32C2.49722 32 1.68663 31.6521 1.01267 30.9564C0.338704 30.2607 0.00114815 29.4234 0 28.4444V3.55556C0 2.57778 0.337556 1.74104 1.01267 1.04533C1.68778 0.34963 2.49837 0.00118519 3.44444 0H15.5V3.55556H3.44444V28.4444H15.5V32H3.44444ZM22.3889 24.8889L20.0208 22.3111L24.4125 17.7778H10.3333V14.2222H24.4125L20.0208 9.68889L22.3889 7.11111L31 16L22.3889 24.8889Z" fill="#FF2A2A"/>
              </svg>
              Cerrar sesion
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>

  <div class="titulo-pagina w-fit text-zinc-900 text-4xl font-semibold font-['Inter'] pb-2 mb-6 border-b-2 border-black">Configuracion</div>

  <div class="contenido-pagina flex gap-6 items-start font-['Inter']">
    <div class="w-64 bg-white rounded-2xl border border-sky-500 shadow-[0px_4px_20px_2px_rgba(0,0,0,0.15)] p-5 flex flex-col gap-1 shrink-0">
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>
        Mi usuario
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        Notificaciones
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/></svg>
        Seguridad
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl text-black/70">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.04-1.56V3a2 2 0 0 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 0 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15Z"/></svg>
        Configuracion
      </div>
      <div class="flex items-center gap-3 px-3 py-3 rounded-xl bg-sky-500 text-white font-medium">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
        Disponibilidad
      </div>

      <div class="flex-1"></div>
      <hr class="border-zinc-200 my-2" />
      <button class="flex items-center gap-3 px-3 py-3 rounded-xl bg-red-100 text-red-500 font-medium" @click="emit('ir-a-bienvenida')">
        <svg  cursor="pointer" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Cerrar sesion
      </button>
    </div>

    <div class="flex-1 bg-white rounded-2xl border border-sky-500 shadow-[0px_4px_20px_2px_rgba(0,0,0,0.15)] p-8">
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
          <button class="px-5 py-2.5 rounded-xl bg-zinc-200 font-medium hover:bg-zinc-300" @click="cancelarCambios">Cancelar</button>
          <button
            class="px-5 py-2.5 rounded-xl bg-sky-500 text-white font-medium hover:bg-sky-600 disabled:opacity-50"
            :disabled="guardando"
            @click="guardarCambios"
          >{{ guardando ? 'Guardando...' : 'Guardar cambios' }}</button>
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
