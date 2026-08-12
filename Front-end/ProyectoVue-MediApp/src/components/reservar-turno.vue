<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-calendario-usuario'])
const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Especialidad = {
  id_especialidad: number
  nombre_especialidad: string
}

type Medico = {
  id: number
  nombre: string
  apellido: string
  telefono: string | null
  mail: string
  especialidad_id: number | null
  especialidad: Especialidad | null
}

const medicos = ref<Medico[]>([])
const cargandoMedicos = ref(true)
const errorMedicos = ref('')

const especialidadSeleccionada = ref<number | null>(null)
const medicoSeleccionado = ref<Medico | null>(null)

async function cargarMedicos() {
  cargandoMedicos.value = true
  errorMedicos.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos`)
    if (!res.ok) throw new Error()
    medicos.value = await res.json()
  } catch {
    errorMedicos.value = 'No se pudieron cargar los profesionales. Intentá de nuevo más tarde.'
  } finally {
    cargandoMedicos.value = false
  }
}

onMounted(cargarMedicos)

const especialidadesDisponibles = computed<Especialidad[]>(() => {
  const vistas = new Map<number, Especialidad>()
  for (const m of medicos.value) {
    if (m.especialidad && !vistas.has(m.especialidad.id_especialidad)) {
      vistas.set(m.especialidad.id_especialidad, m.especialidad)
    }
  }
  return [...vistas.values()].sort((a, b) => a.nombre_especialidad.localeCompare(b.nombre_especialidad))
})

const medicosFiltrados = computed(() => {
  if (especialidadSeleccionada.value === null) return medicos.value
  return medicos.value.filter(m => m.especialidad_id === especialidadSeleccionada.value)
})

function elegirEspecialidad(id: number) {
  especialidadSeleccionada.value = especialidadSeleccionada.value === id ? null : id
  if (medicoSeleccionado.value && medicoSeleccionado.value.especialidad_id !== especialidadSeleccionada.value) {
    medicoSeleccionado.value = null
  }
}

function elegirMedico(m: Medico) {
  medicoSeleccionado.value = medicoSeleccionado.value?.id === m.id ? null : m
}

const coloresAvatar = ['#E0645C', '#6CC26A', '#E0A75C', '#5C9EE0', '#9C6CE0', '#5CC2B0']
function colorAvatar(id: number) {
  return coloresAvatar[id % coloresAvatar.length]
}
function iniciales(m: Medico) {
  return `${m.nombre.charAt(0)}${m.apellido.charAt(0)}`.toUpperCase()
}

const pasoActual = ref(1)

function claseCirculoPaso(n: number) {
  if (pasoActual.value === n) return 'bg-sky-500 text-white'
  if (pasoActual.value > n) return 'bg-white border-2 border-sky-500 text-sky-500'
  return 'border-2 border-zinc-300 text-zinc-400'
}
function claseTextoPaso(n: number) {
  return pasoActual.value >= n ? 'text-black' : 'text-zinc-400'
}

function continuarAPaso2() {
  if (!medicoSeleccionado.value) return
  pasoActual.value = 2
  cargarHorarios(medicoSeleccionado.value.id)
}
function volverAPaso1() {
  pasoActual.value = 1
}

function continuarAPaso3() {
  if (!diaSeleccionado.value || !horaSeleccionada.value) return
  pasoActual.value = 3
}
function volverAPaso2() {
  pasoActual.value = 2
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
  const ultimoDiaMesAnterior = new Date(añoActual.value, mesActual.value, 0).getDate()
  const resultado = []

  for (let i = offset; i > 0; i--) {
    resultado.push({ dia: ultimoDiaMesAnterior - i + 1, otroMes: true })
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

const diaSeleccionado = ref<number | null>(null)

function elegirDia(celda: { dia?: number; otroMes?: boolean }) {
  if (celda.otroMes || celda.dia === undefined) return
  diaSeleccionado.value = celda.dia
  horaSeleccionada.value = null
}

// --- Horarios disponibles del médico ---
// El backend guarda horarios semanales fijos (dia_semana 0=Lunes ... 6=Domingo, igual que Date.weekday() de Python).

type Horario = {
  id: number
  dia_semana: number
  hora: number
}

const horarios = ref<Horario[]>([])
const cargandoHorarios = ref(false)
const errorHorarios = ref('')
const horaSeleccionada = ref<number | null>(null)

async function cargarHorarios(medicoId: number) {
  cargandoHorarios.value = true
  errorHorarios.value = ''
  horarios.value = []
  horaSeleccionada.value = null
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/medicos/${medicoId}/horarios`)
    if (!res.ok) throw new Error()
    horarios.value = await res.json()
  } catch {
    errorHorarios.value = 'No se pudieron cargar los horarios. Intentá de nuevo más tarde.'
  } finally {
    cargandoHorarios.value = false
  }
}

const diaSemanaSeleccionado = computed(() => {
  if (diaSeleccionado.value === null) return null
  const fecha = new Date(añoActual.value, mesActual.value, diaSeleccionado.value)
  return (fecha.getDay() + 6) % 7
})

const horariosDelDia = computed(() => {
  if (diaSemanaSeleccionado.value === null) return []
  return horarios.value
    .filter(h => h.dia_semana === diaSemanaSeleccionado.value)
    .sort((a, b) => a.hora - b.hora)
})

function horaTexto(h: Horario) {
  return `${String(h.hora).padStart(2, '0')}:00`
}

function elegirHora(h: Horario) {
  horaSeleccionada.value = horaSeleccionada.value === h.hora ? null : h.hora
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
        <button class="campoo">Reservar Turno</button>
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

          <button href="#" style="margin-top: auto;">
            <div class="barra-dentro-cerrar w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 31 32" fill="none" style="flex-shrink: 0;">
                  <path d="M3.44444 32C2.49722 32 1.68663 31.6521 1.01267 30.9564C0.338704 30.2607 0.00114815 29.4234 0 28.4444V3.55556C0 2.57778 0.337556 1.74104 1.01267 1.04533C1.68778 0.34963 2.49837 0.00118519 3.44444 0H15.5V3.55556H3.44444V28.4444H15.5V32H3.44444ZM22.3889 24.8889L20.0208 22.3111L24.4125 17.7778H10.3333V14.2222H24.4125L20.0208 9.68889L22.3889 7.11111L31 16L22.3889 24.8889Z" fill="#FF2A2A"/>
                </svg>
                <button @click="emit('ir-a-bienvenida')">Cerrar sesion</button>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <div style="margin-top: 7.5rem; margin-left: 2.5rem; margin-right: 2.5rem; display: flex; flex-direction: column;">

      <div class="w-full max-w-[64rem] mx-auto">
        <div class="w-fit text-[2.4rem] font-normal font-['Inter'] leading-[74.99px] pb-2 border-b-2 border-black">Reservar turno</div>
      </div>

      <div class="flex items-center gap-4 mt-8 mb-6 w-full max-w-[64rem] mx-auto font-['Inter']">
        <div class="flex items-center gap-4">
          <div class="size-12 shrink-0 rounded-full flex items-center justify-center text-xl transition-colors" :class="claseCirculoPaso(1)">1</div>
          <span class="text-2xl whitespace-nowrap transition-colors" :class="claseTextoPaso(1)">Profesional</span>
        </div>
        <div class="flex-1 h-px bg-zinc-300 min-w-[3rem]"></div>
        <div class="flex items-center gap-4">
          <div class="size-12 shrink-0 rounded-full flex items-center justify-center text-xl transition-colors" :class="claseCirculoPaso(2)">2</div>
          <span class="text-2xl whitespace-nowrap transition-colors" :class="claseTextoPaso(2)">Fecha y hora</span>
        </div>
        <div class="flex-1 h-px bg-zinc-300 min-w-[3rem]"></div>
        <div class="flex items-center gap-4">
          <div class="size-12 shrink-0 rounded-full flex items-center justify-center text-xl transition-colors" :class="claseCirculoPaso(3)">3</div>
          <span class="text-2xl whitespace-nowrap transition-colors" :class="claseTextoPaso(3)">Confirmar</span>
        </div>
      </div>

      <div class="bg-white rounded-[1.5rem] shadow-[0px_4px_30.100000381469727px_8px_rgba(0,0,0,0.46)] border border-sky-500 p-8 w-full max-w-[64rem] mx-auto flex flex-col gap-6 font-['Inter']">

        <Transition name="fade" mode="out-in">
          <div v-if="pasoActual === 1" key="paso1" class="flex flex-col gap-6">
            <div v-if="especialidadesDisponibles.length">
              <h2 class="text-xl mb-3">Especialidad</h2>
              <div class="flex flex-wrap gap-3">
                <button
                  v-for="esp in especialidadesDisponibles" :key="esp.id_especialidad"
                  @click="elegirEspecialidad(esp.id_especialidad)"
                  class="px-5 py-2 rounded-full transition-colors"
                  :class="especialidadSeleccionada === esp.id_especialidad ? 'bg-sky-500 text-white' : 'bg-sky-100 hover:bg-sky-200'"
                >{{ esp.nombre_especialidad }}</button>
              </div>
            </div>

            <div>
              <h2 class="text-xl mb-3">Profesional</h2>

              <p v-if="cargandoMedicos" class="text-zinc-400">Cargando profesionales...</p>
              <p v-else-if="errorMedicos" class="text-red-500">{{ errorMedicos }}</p>
              <p v-else-if="!medicosFiltrados.length" class="text-zinc-400">No hay profesionales disponibles para esta especialidad.</p>

              <div v-else class="flex flex-col gap-2">
                <button
                  v-for="m in medicosFiltrados" :key="m.id"
                  @click="elegirMedico(m)"
                  class="flex items-center gap-3 border-2 rounded-2xl p-2.5 text-left transition-colors"
                  :class="medicoSeleccionado?.id === m.id ? 'border-sky-500 bg-sky-50' : 'border-sky-200 hover:border-sky-400'"
                >
                  <div class="size-10 shrink-0 rounded-full flex items-center justify-center text-white text-sm font-medium" :style="{ backgroundColor: colorAvatar(m.id) }">{{ iniciales(m) }}</div>
                  <div class="flex-1">
                    <div class="font-medium">{{ m.nombre }} {{ m.apellido }}</div>
                    <div class="text-sm text-zinc-500">{{ m.especialidad?.nombre_especialidad ?? 'Sin especialidad' }}</div>
                    <div class="text-sm text-zinc-500">{{ m.mail }}</div>
                  </div>
                </button>
              </div>
            </div>

            <div class="flex justify-end mt-2">
              <button
                @click="continuarAPaso2"
                class="px-8 py-3 rounded-xl bg-sky-500 text-white font-medium hover:bg-sky-600 disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!medicoSeleccionado"
              >Continuar</button>
            </div>
          </div>

          <div v-else-if="pasoActual === 2" key="paso2" class="flex flex-col gap-6">
            <div>
              <h2 class="text-xl mb-3">Fecha</h2>
              <div class="w-full mx-auto rounded-2xl border-2 border-sky-200 p-7">
                <div class="flex items-center justify-between mb-4">
                  <button @click="mesAnterior" class="size-11 rounded-xl border border-zinc-300 flex items-center justify-center text-lg hover:bg-sky-50">←</button>
                  <span class="text-3xl font-medium">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
                  <button @click="mesSiguiente" class="size-11 rounded-xl border border-zinc-300 flex items-center justify-center text-lg hover:bg-sky-50">→</button>
                </div>
                <div class="grid grid-cols-7 gap-y-4 text-center">
                  <button
                    v-for="(celda, i) in celdas" :key="i"
                    @click="elegirDia(celda)"
                    :disabled="celda.otroMes"
                    class="size-11 mx-auto rounded-lg text-xl transition-colors"
                    :class="[
                      celda.otroMes ? 'text-zinc-300 cursor-default' : 'text-black font-medium hover:bg-sky-100',
                      !celda.otroMes && celda.dia === diaSeleccionado ? 'bg-sky-500 text-white hover:bg-sky-500' : '',
                      !celda.otroMes && celda.hoy && celda.dia !== diaSeleccionado ? 'text-sky-500 font-semibold' : ''
                    ]"
                  >{{ celda.dia }}</button>
                </div>
              </div>
            </div>
            <div>
              <div class="w-fit text-[1.5rem] font-normal font-['Inter'] pb-1 mb-4 border-b-2 border-black">Horarios Disponibles</div>

              <p v-if="!diaSeleccionado" class="text-zinc-400">Elegí un día en el calendario para ver los horarios.</p>
              <p v-else-if="cargandoHorarios" class="text-zinc-400">Cargando horarios...</p>
              <p v-else-if="errorHorarios" class="text-red-500">{{ errorHorarios }}</p>
              <p v-else-if="!horariosDelDia.length" class="text-zinc-400">No hay horarios disponibles para este día.</p>

              <div v-else class="grid gap-3" style="grid-template-columns: repeat(auto-fill, minmax(7rem, 1fr));">
                <button
                  v-for="h in horariosDelDia" :key="h.id"
                  @click="elegirHora(h)"
                  class="px-7 py-3.5 rounded-xl border-2 text-lg font-medium text-center transition-colors"
                  :class="horaSeleccionada === h.hora ? 'bg-sky-500 border-sky-500 text-white' : 'border-sky-500 text-sky-600 hover:bg-sky-50'"
                >{{ horaTexto(h) }}</button>
              </div>
            </div>

            <div class="flex w-full justify-between mt-2">
              <button @click="volverAPaso1" class="px-6 py-3 bg-sky-100 rounded-xl border-2 border-sky-500 text-sky-600 hover:bg-sky-50">Atrás</button>
              <button @click="continuarAPaso3"
                v-if="diaSeleccionado && horaSeleccionada"
                class="px-8 py-3 rounded-xl bg-sky-500 text-white font-medium hover:bg-sky-600"
              >Continuar</button>
            </div>
          </div>

          <div v-else key="paso3" class="flex flex-col gap-6">
            <div>
              
            </div>

            <div class="flex w-full justify-start mt-2">
              <button @click="volverAPaso2" class="px-6 py-3 bg-sky-100 rounded-xl border-2 border-sky-500 text-sky-600 hover:bg-sky-50">Atrás</button>
            </div>
          </div>

        </Transition>

      </div>

    </div>
</div>
</template>

<style>
</style>
