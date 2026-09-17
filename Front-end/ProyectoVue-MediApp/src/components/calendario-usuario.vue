<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-reservar-turno', 'ir-a-calendario-usuario'])

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

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
const nombresDia = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

const seleccionado = ref(new Date())

function correrDias(n: number) {
  return new Date(
    seleccionado.value.getFullYear(),
    seleccionado.value.getMonth(),
    seleccionado.value.getDate() + n
  )
}

const anterior = computed(() => correrDias(-1))
const siguiente = computed(() => correrDias(1))

function diaAnterior() {
  seleccionado.value = correrDias(-1)
}

function diaSiguiente() {
  seleccionado.value = correrDias(1)
}

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

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const turnos = ref<Turno[]>([])

async function cargarTurnos() {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) return
    turnos.value = await res.json()
  } catch {
  }
}

onMounted(cargarTurnos)

function esMismoDia(fechaHora: string, dia: Date) {
  const f = new Date(fechaHora)
  return f.getFullYear() === dia.getFullYear() && f.getMonth() === dia.getMonth() && f.getDate() === dia.getDate()
}

const CANTIDAD_SLOTS = 3

const turnosDelDia = computed(() => {
  return turnos.value
    .filter(t => t.estado?.estado === 'aceptado' && esMismoDia(t.fecha_hora, seleccionado.value))
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
    .slice(0, CANTIDAD_SLOTS)
})

const slots = computed(() => {
  const lista: (Turno | null)[] = [...turnosDelDia.value]
  while (lista.length < CANTIDAD_SLOTS) lista.push(null)
  return lista
})

function formatearHoraTurno(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}
function especialidadTurno(t: Turno) {
  return t.medico.especialidades[0]?.nombre_especialidad ?? 'Consulta'
}
function nombreMedicoTurno(t: Turno) {
  return `${t.medico.nombre} ${t.medico.apellido}`
}
</script>

<template>
  <div>
    
    <div class="navbar">
      <button  @click="emit('ir-a-principal-usuario')">
        <div class="navbar-logo" style="cursor:pointer">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

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
                <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 31 32" fill="none">
                  <path d="M15.5 0C17.5554 0 19.5267 0.842854 20.9801 2.34315C22.4335 3.84344 23.25 5.87827 23.25 8C23.25 10.1217 22.4335 12.1566 20.9801 13.6569C19.5267 15.1571 17.5554 16 15.5 16C13.4446 16 11.4733 15.1571 10.0199 13.6569C8.56651 12.1566 7.75 10.1217 7.75 8C7.75 5.87827 8.56651 3.84344 10.0199 2.34315C11.4733 0.842854 13.4446 0 15.5 0ZM15.5 4C14.4723 4 13.4867 4.42143 12.76 5.17157C12.0333 5.92172 11.625 6.93913 11.625 8C11.625 9.06087 12.0333 10.0783 12.76 10.8284C13.4867 11.5786 14.4723 12 15.5 12C16.5277 12 17.5133 11.5786 18.24 10.8284C18.9667 10.0783 19.375 9.06087 19.375 8C19.375 6.93913 18.9667 5.92172 18.24 5.17157C17.5133 4.42143 16.5277 4 15.5 4ZM15.5 18C20.6731 18 31 20.66 31 26V32H0V26C0 20.66 10.3269 18 15.5 18ZM15.5 21.8C9.74562 21.8 3.68125 24.72 3.68125 26V28.2H27.3188V26C27.3188 24.72 21.2544 21.8 15.5 21.8Z" fill="black"/>
                </svg>
                Mi cuenta
              </div>
            </div>
          </button>

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

    <div class="cal-contenido">
      <div id="calendario">

        <div class="izq">
          <div class="cal-header">
            <button class="cal-nav-btn" @click="mesAnterior">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>

            <span class="cal-titulo">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
            <button class="cal-nav-btn" @click="mesSiguiente">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none" class="cal-nav-der">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
          </div>

           <div class="calgGrid">
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
              class="calDia"
              :class="{
                'cal-hoy': celda.hoy,
                'cal-otro-mes': celda.otroMes
              }"
            >
              {{ celda.dia }}
            </div>
          </div>
        </div>

        <div class="divisor-v"></div>

        <div class="der">
          <div class="flex items-center justify-between w-full">
            <button @click="diaAnterior">
              <div class="size-20 relative flex items-center justify-center rounded-[2.625rem] border border-black bg-white">
                <svg width="80" height="70" viewBox="0 0 83 82" fill="none">
                  <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
                </svg>
              </div>
            </button>

            <div class="flex flex-col items-center">
              <span class="text-2xl text-gray-400 font-medium">{{ nombresDia[anterior.getDay()] }}</span>
              <span class="text-5xl text-gray-400 font-semibold">{{ anterior.getDate() }}</span>
            </div>

            <div class="flex flex-col items-center">
              <span class="text-2xl text-black font-medium">{{ nombresDia[seleccionado.getDay()] }}</span>
              <span class="text-5xl text-black font-bold">{{ seleccionado.getDate() }}</span>
            </div>

            <div class="flex flex-col items-center">
              <span class="text-2xl text-gray-400 font-medium">{{ nombresDia[siguiente.getDay()] }}</span>
              <span class="text-5xl text-gray-400 font-semibold">{{ siguiente.getDate() }}</span>
            </div>

            <button @click="diaSiguiente">
              <div class="size-20 relative flex items-center justify-center rounded-[2.625rem] border border-black bg-white">
                <svg width="80" height="70" viewBox="0 0 83 82" fill="none" class="rotate-180">
                  <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
                </svg>
              </div>
            </button>
          </div>
          <div class="flex-1 flex flex-col justify-center gap-6 mt-[2%]">
            <div v-for="(t, i) in slots" :key="i" class="w-full flex flex-col items-center" :class="{ 'mt-[2%]': i > 0 }">
              <div
                v-if="t"
                class="w-[100%] h-24 bg-red-400 rounded-2xl flex items-center justify-between px-6"
              >
                <div>
                  <div class="text-2xl font-medium text-black">{{ especialidadTurno(t) }}</div>
                  <div class="text-black/60">{{ nombreMedicoTurno(t) }}</div>
                </div>
                <div class="text-3xl text-black">{{ formatearHoraTurno(t.fecha_hora) }}</div>
              </div>
              <div v-else class="w-[100%] h-24"></div>
              <div class="w-[100%] mt-4 h-0 outline-1 outline-offset-[-0.5px] outline-black/30"></div>
            </div>
          </div>


        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
.cal-contenido {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 6.25rem);
  margin-top: 6.25rem;
}

#calendario {
  width: 71.5rem;
  height: 37.5rem;
  background: #fff;
  border-radius: 1.25rem;
  box-shadow: 0rem 0.25rem 0.66875rem 0.3125rem rgba(0, 0, 0, 0.25);
  border: 0.3125rem solid #2E9CE0;
  display: flex;
  flex-direction: row;
}

.divisor-v {
  width: 0.08125rem;
  background: black;
  align-self: center;
  flex-shrink: 0;
  height: 90%;
  justify-content: center;
}
.izq {
  width: 35%;
}
.der {
  width: 65%;
  display: flex;
  flex-direction: column;
  padding: 3%;
  font-family: 'Inter', sans-serif;
  font-weight: 200;
}

.cal-nav-btn {
  display: flex;
  justify-content: flex-start;
}
.cal-nav-der {
  transform: rotate(180deg);
}
.cal-titulo {
  color: #000;
  text-align: center;
  font-family: Inter;
  font-size: 1.7rem;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}
.calDia {
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.5625rem;
  padding: 0.3125rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  gap: 1.25rem;
}

.calgGrid {
  row-gap: 1.25rem;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 0 1rem;
  flex: 1;
  align-content: start;
}


</style>
