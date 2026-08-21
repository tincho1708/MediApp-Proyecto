<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-reservar-turno'])
const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Paciente = {
  id: number
  nombre: string
  apellido: string
}

type Turno = {
  id_turno: number
  fecha_hora: string
  notas: string | null
  creado_en: string
  id_pacientes: number
  id_medicos: number
  estado: { id: number; estado: string }
  paciente: Paciente
}

function token() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  return sesion.token as string | undefined
}

const turnos = ref<Turno[]>([])
const cargando = ref(true)
const errorCarga = ref('')
const turnoSeleccionadoId = ref<number | null>(null)

const turnosPendientes = computed(() =>
  turnos.value
    .filter(t => t.estado.estado === 'pendiente')
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
)

const turnoSeleccionado = computed(() =>
  turnosPendientes.value.find(t => t.id_turno === turnoSeleccionadoId.value) ?? null
)

async function cargarSolicitudes() {
  cargando.value = true
  errorCarga.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${token()}` },
    })
    if (!res.ok) throw new Error()
    turnos.value = await res.json()
  } catch {
    errorCarga.value = 'No se pudieron cargar las solicitudes. Intentá de nuevo más tarde.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargarSolicitudes)

function seleccionarTurno(t: Turno) {
  turnoSeleccionadoId.value = turnoSeleccionadoId.value === t.id_turno ? null : t.id_turno
}

const coloresAvatar = ['#E0645C', '#6CC26A', '#E0A75C', '#5C9EE0', '#9C6CE0', '#5CC2B0']
function colorAvatar(id: number) {
  return coloresAvatar[id % coloresAvatar.length]
}
function iniciales(p: Paciente) {
  return `${p.nombre.charAt(0)}${p.apellido.charAt(0)}`.toUpperCase()
}

function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()}/${f.getMonth() + 1}`
}
function formatearRangoHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  const inicio = `${pad(f.getHours())}:${pad(f.getMinutes())}`
  const fin = new Date(f.getTime() + 60 * 60 * 1000)
  const finTexto = `${pad(fin.getHours())}:${pad(fin.getMinutes())}`
  return `${inicio}-${finTexto}`
}

function tiempoRelativo(creadoEn: string) {
  const segundos = Math.max(0, Math.floor((Date.now() - new Date(creadoEn + 'Z').getTime()) / 1000))
  const minutos = Math.floor(segundos / 60)
  if (minutos < 1) return 'unos segundos'
  if (minutos < 60) return `${minutos} minuto${minutos === 1 ? '' : 's'}`
  const horas = Math.floor(minutos / 60)
  if (horas < 24) return `${horas} hora${horas === 1 ? '' : 's'}`
  const dias = Math.floor(horas / 24)
  return `${dias} día${dias === 1 ? '' : 's'}`
}

const procesando = ref(false)
const errorAccion = ref('')

async function resolverTurno(accion: 'aceptar' | 'rechazar') {
  if (!turnoSeleccionado.value) return
  procesando.value = true
  errorAccion.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/${turnoSeleccionado.value.id_turno}/${accion}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token()}` },
    })
    const data = await res.json()
    if (!res.ok) {
      errorAccion.value = data.detail || 'No se pudo actualizar la solicitud.'
      return
    }
    turnos.value = turnos.value.map(t => (t.id_turno === data.id_turno ? data : t))
    turnoSeleccionadoId.value = null
  } catch {
    errorAccion.value = 'No se pudo conectar al servidor.'
  } finally {
    procesando.value = false
  }
}
</script>

<template>
    <div class="navbar">
      <button  @click="emit('ir-a-principal')">
        <div class="navbar-logo" style="cursor:pointer">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
        <button class="campoo">Mis pacientes</button>
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

          <button href="#">
            <div id="barra-dentro" class="w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="21" viewBox="0 0 37 32" fill="none" style="flex-shrink: 0;">
                  <path d="M37 0V14.7692C36.8555 14.4744 36.6989 14.1603 36.5303 13.8269C36.3617 13.4936 36.175 13.1667 35.9702 12.8462C35.7655 12.5256 35.5547 12.2051 35.3379 11.8846C35.1211 11.5641 34.9043 11.2949 34.6875 11.0769V4.92308L18.5 13.5385L2.3125 4.92308V22.1538H19.6562L20.8125 24.6154H0V0H37ZM34.4165 2.46154H2.5835L18.5 10.9423L34.4165 2.46154ZM32.6641 23.1346C33.3265 23.5064 33.9227 23.9615 34.4526 24.5C34.9826 25.0385 35.4403 25.641 35.8257 26.3077C36.2111 26.9744 36.5002 27.6795 36.6929 28.4231C36.8856 29.1667 36.988 29.9487 37 30.7692V32H34.6875V30.7692C34.6875 29.9231 34.5369 29.1282 34.2358 28.3846C33.9347 27.641 33.5192 26.9936 32.9893 26.4423C32.4593 25.891 31.8451 25.4487 31.1465 25.1154C30.4479 24.7821 29.7012 24.6154 28.9062 24.6154C28.1113 24.6154 27.3646 24.7756 26.666 25.0962C25.9674 25.4167 25.3532 25.859 24.8232 26.4231C24.2933 26.9872 23.8778 27.641 23.5767 28.3846C23.2756 29.1282 23.125 29.9231 23.125 30.7692V32H20.8125V30.7692C20.8125 29.9615 20.9089 29.1859 21.1016 28.4423C21.2943 27.6987 21.5833 26.9936 21.9688 26.3269C22.3542 25.6603 22.8118 25.0577 23.3418 24.5192C23.8717 23.9808 24.474 23.5192 25.1484 23.1346C24.498 22.5449 23.9982 21.8462 23.6489 21.0385C23.2996 20.2308 23.125 19.3718 23.125 18.4615C23.125 17.6154 23.2756 16.8205 23.5767 16.0769C23.8778 15.3333 24.2873 14.6859 24.8052 14.1346C25.3231 13.5833 25.9373 13.141 26.6479 12.8077C27.3586 12.4744 28.1113 12.3077 28.9062 12.3077C29.7012 12.3077 30.4479 12.4679 31.1465 12.7885C31.8451 13.109 32.4533 13.5513 32.9712 14.1154C33.4891 14.6795 33.9046 15.3333 34.2178 16.0769C34.5309 16.8205 34.6875 17.6154 34.6875 18.4615C34.6875 19.359 34.5129 20.2115 34.1636 21.0192C33.8143 21.8269 33.3145 22.5321 32.6641 23.1346ZM25.4375 18.4615C25.4375 18.9744 25.5278 19.4551 25.7085 19.9038C25.8892 20.3526 26.1361 20.7436 26.4492 21.0769C26.7624 21.4103 27.1297 21.6731 27.5513 21.8654C27.9728 22.0577 28.4245 22.1538 28.9062 22.1538C29.388 22.1538 29.8397 22.0577 30.2612 21.8654C30.6828 21.6731 31.0501 21.4103 31.3633 21.0769C31.6764 20.7436 31.9233 20.3526 32.104 19.9038C32.2847 19.4551 32.375 18.9744 32.375 18.4615C32.375 17.9487 32.2847 17.4679 32.104 17.0192C31.9233 16.5705 31.6764 16.1795 31.3633 15.8462C31.0501 15.5128 30.6828 15.25 30.2612 15.0577C29.8397 14.8654 29.388 14.7692 28.9062 14.7692C28.4245 14.7692 27.9728 14.8654 27.5513 15.0577C27.1297 15.25 26.7624 15.5128 26.4492 15.8462C26.1361 16.1795 25.8892 16.5705 25.7085 17.0192C25.5278 17.4679 25.4375 17.9487 25.4375 18.4615Z" fill="black"/>
                </svg>
                Solicitudes
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
    
    <div class="titulo-pagina w-fit text-zinc-900 text-5xl font-semibold font-['Inter'] pb-2 mb-6 border-b-2 border-black">Solicitudes</div>

    <div class="contenido-pagina">

      <div class="flex flex-col w-[800px] h-[503px] bg-white rounded-[20px] shadow-[0px_4px_30.100000381469727px_0px_rgba(0,0,0,0.46)] border border-sky-500 overflow-hidden">
        <div class="flex flex-row gap-30 px-8 pt-5 pb-3">
          <div class="ml-15 w-36 h-7 justify-start text-black/50 text-2xl font-medium font-['Inter']">Paciente</div>
          <div class="w-36 h-7 justify-start text-black/50 text-2xl font-medium font-['Inter']">Motivo</div>
          <div class="ml-10 w-36 h-7 justify-start text-black/50 text-2xl font-medium font-['Inter']">Fecha</div>
        </div>

        <div class="flex-1 overflow-y-auto px-3 pb-3">
          <p v-if="cargando" class="text-zinc-400 px-5 py-4">Cargando solicitudes...</p>
          <p v-else-if="errorCarga" class="text-red-500 px-5 py-4">{{ errorCarga }}</p>
          <p v-else-if="!turnosPendientes.length" class="text-zinc-400 px-5 py-4">No tenés solicitudes pendientes.</p>

          <button
            v-for="t in turnosPendientes" :key="t.id_turno"
            @click="seleccionarTurno(t)"
            class="fila-solicitud w-full flex items-center gap-4 rounded-xl px-5 py-3 text-left transition-colors"
            :class="turnoSeleccionadoId === t.id_turno ? 'bg-sky-100' : 'hover:bg-zinc-50'"
          >
            <div class="size-10 shrink-0 rounded-full flex items-center justify-center text-white text-sm font-medium" :style="{ backgroundColor: colorAvatar(t.paciente.id) }">{{ iniciales(t.paciente) }}</div>
            <div class="w-40 shrink-0 font-medium">{{ t.paciente.nombre }} {{ t.paciente.apellido }}</div>
            <div class="flex-1 text-zinc-500 truncate">{{ t.notas || 'Sin motivo especificado' }}</div>
            <div class="shrink-0 text-right text-sm text-zinc-500">
              {{ formatearFecha(t.fecha_hora) }}
              <div class="font-semibold text-zinc-700">{{ formatearRangoHora(t.fecha_hora) }}</div>
            </div>
            <span class="text-zinc-400">›</span>
          </button>
        </div>
      </div>

      <div class="flex flex-col w-[501px] h-[503px] bg-white rounded-[20px] shadow-[0px_4px_30.100000381469727px_0px_rgba(0,0,0,0.46)] border border-sky-500 p-8">
        <div v-if="!turnoSeleccionado" class="flex-1 flex items-center justify-center text-center text-zinc-400 text-xl font-['Inter']">
          Selecciona una solicitud para visualizarla
        </div>

        <template v-else>
          <div class="flex items-center gap-4">
            <div class="size-16 shrink-0 rounded-full flex items-center justify-center text-white text-2xl font-medium" :style="{ backgroundColor: colorAvatar(turnoSeleccionado.paciente.id) }">{{ iniciales(turnoSeleccionado.paciente) }}</div>
            <div class="text-2xl font-semibold font-['Inter']">{{ turnoSeleccionado.paciente.nombre }} {{ turnoSeleccionado.paciente.apellido }}</div>
          </div>

          <div class="mt-6 text-zinc-900 text-xl font-['Inter']">Motivo de la consulta</div>
          <div class="mt-2 bg-sky-100 rounded-2xl p-5 text-zinc-800 min-h-[10rem]">{{ turnoSeleccionado.notas || 'Sin motivo especificado' }}</div>

          <div class="mt-6 text-zinc-500 font-['Inter']">Solicitado hace</div>
          <div class="text-xl font-medium">{{ tiempoRelativo(turnoSeleccionado.creado_en) }}</div>

          <p v-if="errorAccion" class="mt-4 text-red-500 text-center">{{ errorAccion }}</p>

          <div class="mt-auto flex justify-between gap-4 pt-6">
            <button
              @click="resolverTurno('rechazar')"
              :disabled="procesando"
              class="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-red-100 text-red-500 font-medium hover:bg-red-200 disabled:opacity-40"
            >✕ Rechazar</button>
            <button
              @click="resolverTurno('aceptar')"
              :disabled="procesando"
              class="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-green-100 text-green-600 font-medium hover:bg-green-200 disabled:opacity-40"
            >✓ Aceptar</button>
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
  display: flex;
  flex-direction: row;
  gap: 2.5rem;
}
</style>