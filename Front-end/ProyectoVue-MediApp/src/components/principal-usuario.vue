<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-chatbot', 'ir-a-calendario-usuario', 'ir-a-reservar-turno'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Turno = {
  id_turno: number
  fecha_hora: string
  estado: { estado: string }
  medico: {
    nombre: string
    apellido: string
    especialidades: { nombre_especialidad: string }[]
  }
}

const turnos = ref<Turno[]>([])
const cargandoTurnos = ref(true)
const errorTurnos = ref('')

const proximosTurnos = computed(() => {
  const ahora = Date.now()
  return turnos.value
    .filter(t => t.estado?.estado === 'aceptado' && new Date(t.fecha_hora).getTime() >= ahora)
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
    .slice(0, 4)
})

async function cargarTurnos(silencioso = false) {
  if (!silencioso) {
    cargandoTurnos.value = true
    errorTurnos.value = ''
  }
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) throw new Error()
    turnos.value = await res.json()
  } catch {
    if (!silencioso) errorTurnos.value = 'No se pudieron cargar los turnos.'
  } finally {
    if (!silencioso) cargandoTurnos.value = false
  }
}

onMounted(() => cargarTurnos())

let intervaloTurnos: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  intervaloTurnos = setInterval(() => cargarTurnos(true), 6000)
})
onBeforeUnmount(() => {
  if (intervaloTurnos !== undefined) clearInterval(intervaloTurnos)
})

function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()}/${f.getMonth() + 1}`
}
function formatearHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}
function etiquetaTurno(t: Turno) {
  const especialidad = t.medico.especialidades[0]?.nombre_especialidad
  return especialidad ? `Turno ${especialidad.toLowerCase()}` : `Turno con ${t.medico.nombre} ${t.medico.apellido}`
}

const hoy = new Date()
const mesActual = ref(hoy.getMonth())
const añoActual = ref(hoy.getFullYear())

const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

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
  const primerDia = new Date(añoActual.value, mesActual.value, 1).getDay()
  const offset = (primerDia + 6) % 7
  const resultado = []

  for (let i = 0; i < offset; i++) {
    resultado.push({ otroMes: true })
  }

  for (let d = 1; d <= ultimoDia; d++) {
    resultado.push({
      dia: d,
      hoy: d === hoy.getDate() && mesActual.value === hoy.getMonth() && añoActual.value === hoy.getFullYear(),
    })
  }

  let siguiente = 1
  while (resultado.length % 7 !== 0) {
    resultado.push({ dia: siguiente, otroMes: true })
    siguiente++
  }

  return resultado
})
</script>

<template>
  <div>
    <div class="navbar">
      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-reservar-turno')">Reservar Turno</button>
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
        <button class="campoo">Profesionales</button>
        <button class="campoo">Notificaciones</button>

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

    <div class="bienvenida">Bienvenido, {{ nombreUsuario }}</div>

    <div class="main-layout">
      <div class="main-izquierdo" style="margin-left: 2.5rem; height: 30.25rem;">

        <div class="w-[40.9375rem] h-full bg-white rounded-[1.25rem] shadow-[0rem_0.25rem_0.66875rem_0.3125rem_rgba(0,0,0,0.25)] border-[0.3125rem] border-sky-500 flex flex-col" style="padding: 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.625rem;" class="shrink-0">
            <div class="w-16 h-16 rounded-2xl border-2 border-sky-500 flex items-center justify-center shrink-0">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="5" width="18" height="16" rx="2"/>
                <path d="M16 3v4M8 3v4M3 10h18"/>
              </svg>
            </div>
            <div style="color: black; margin-left: 10px; font-size: 2.175rem; font-weight: 700; font-family: 'Inter', sans-serif;">Proximos turnos</div>
          </div>

          <p v-if="cargandoTurnos" class="text-zinc-400 ml-8 mt-4 text-2xl">Cargando turnos...</p>
          <p v-else-if="errorTurnos" class="text-red-500 ml-8 mt-4">{{ errorTurnos }}</p>
          <p v-else-if="!proximosTurnos.length" class="text-zinc-400 text-[1.7rem] ml-8 mt-4">No tenés turnos próximos.</p>

          <div v-else class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-6 mt-7">
            <div v-for="(t, idx) in proximosTurnos" :key="t.id_turno" class="flex flex-row items-center gap-6 ml-8 font-['Inter'] cursor-pointer group">
              <div
                class="flex items-center justify-center w-20 h-20 shrink-0 rounded-[1.5rem] text-white"
                :class="idx % 2 === 0 ? 'bg-red-400' : 'bg-sky-500'"
              >
                <div class="text-2xl font-bold">{{ formatearFecha(t.fecha_hora) }}</div>
              </div>

              <div class="flex-1 min-w-0">
                <div class="text-2xl font-bold text-black/70 truncate">{{ etiquetaTurno(t) }}</div>
                <div class="flex items-center gap-2 mt-1 text-black font-semibold text-lg">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>
                  {{ formatearHora(t.fecha_hora) }}
                </div>
              </div>

              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="shrink-0 group-hover:stroke-sky-500 transition-colors">
                <path d="M9 6l6 6-6 6"/>
              </svg>
            </div>
          </div>
        </div>
        
      </div>

      <div class="div-derecho" style="margin-top: 0;">
        <div class="calendario">
          <div class="cal-header">
            <button class="cal-nav-btn" @click="mesAnterior">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
            <span class="cal-titulo">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
            <button class="cal-nav-btn" @click="mesSiguiente">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none" style="transform:rotate(180deg)">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
          </div>

          <div class="cal-grid">
            <div class="cal-nombre-dia">LU</div>
            <div class="cal-nombre-dia">MA</div>
            <div class="cal-nombre-dia">MI</div>
            <div class="cal-nombre-dia">JU</div>
            <div class="cal-nombre-dia">VI</div>
            <div class="cal-nombre-dia">SA</div>
            <div class="cal-nombre-dia">DO</div>

            <div
              v-for="(celda, i) in celdas"
              :key="i"
              class="cal-dia"
              :class="{
                'cal-hoy': celda.hoy,
                'cal-otro-mes': celda.otroMes
              }"
            >
              {{ celda.dia }}
            </div>
          </div>

          <button class="cal-ver-completo" @click="emit('ir-a-calendario-usuario')">Ver calendario completo</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
