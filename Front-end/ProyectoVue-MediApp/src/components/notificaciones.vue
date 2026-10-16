<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-calendario-usuario', 'ir-a-reservar-turno', 'ir-a-mi-usuario-paciente', 'ir-a-notificaciones'])

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type NotificacionPaciente = {
  id: number
  id_turno: number
  mensaje: string
  leida: boolean
  fecha: string
}

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const notificaciones = ref<NotificacionPaciente[]>([])
const cargando = ref(true)
const error = ref('')

async function cargarNotificaciones() {
  cargando.value = true
  error.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/notificaciones/paciente`, {
      headers: { Authorization: `Bearer ${sesion.token}` },
    })
    if (!res.ok) throw new Error()
    notificaciones.value = await res.json()
    marcarTodasComoLeidas()
  } catch {
    error.value = 'No se pudieron cargar las notificaciones.'
  } finally {
    cargando.value = false
  }
}

async function marcarTodasComoLeidas() {
  for (const n of notificaciones.value) {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/notificaciones/paciente/${n.id}/leer`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${sesion.token}` },
      })
    } catch {
    }
  }
}

onMounted(cargarNotificaciones)

const filtro = ref<'todos' | 'turnos' | 'recordatorios'>('todos')

const notificacionesFiltradas = computed(() => {
  if (filtro.value === 'turnos') return notificaciones.value
  if (filtro.value === 'recordatorios') return []
  return notificaciones.value
})

function formatearFecha(fecha: string) {
  const f = new Date(fecha)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getDate())}/${pad(f.getMonth() + 1)} - ${pad(f.getHours())}:${pad(f.getMinutes())}`
}
</script>

<template>
  <div>
    <div class="navbar">
      <button @click="emit('ir-a-principal-usuario')">
        <div class="navbar-logo" style="cursor:pointer">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-reservar-turno')">Reservar Turno</button>
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
        <button class="campoo">Profesionales</button>
        <button class="campoo" @click="emit('ir-a-notificaciones')">Notificaciones</button>

        <button @click.stop="esta = !esta" class="barra">
          <div class="w-12 h-9 relative">
            <div class="w-12 border-t-2 border-black absolute left-0 top-0"></div>
            <div class="w-12 border-t-2 border-black absolute left-0 top-[1rem]"></div>
            <div class="w-12 border-t-2 border-black absolute left-0 top-[2rem]"></div>
          </div>
        </button>

        <div :class="['barra-desplegable', { 'barra-abierta': esta }]" @click.stop>
          <button href="#" @click="emit('ir-a-mi-usuario-paciente')">
            <div id="barra-dentro" class="w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" style="flex-shrink: 0; width:1.375rem; height:1.375rem;">
                  <path d="M11.6219 32L10.9851 26.88C10.6401 26.7467 10.3154 26.5867 10.0107 26.4C9.70614 26.2133 9.40736 26.0133 9.11443 25.8L4.37811 27.8L0 20.2L4.0995 17.08C4.07297 16.8933 4.0597 16.7136 4.0597 16.5408V15.4608C4.0597 15.2869 4.07297 15.1067 4.0995 14.92L0 11.8L4.37811 4.2L9.11443 6.2C9.4063 5.98667 9.71144 5.78667 10.0299 5.6C10.3483 5.41333 10.6667 5.25333 10.9851 5.12L11.6219 0H20.3781L21.0149 5.12C21.3599 5.25333 21.6852 5.41333 21.9908 5.6C22.2965 5.78667 22.5948 5.98667 22.8856 6.2L27.6219 4.2L32 11.8L27.9005 14.92C27.927 15.1067 27.9403 15.2869 27.9403 15.4608V16.5392C27.9403 16.7131 27.9138 16.8933 27.8607 17.08L31.9602 20.2L27.5821 27.8L22.8856 25.8C22.5937 26.0133 22.2886 26.2133 21.9701 26.4C21.6517 26.5867 21.3333 26.7467 21.0149 26.88L20.3781 32H11.6219ZM14.408 28.8H17.5522L18.1095 24.56C18.932 24.3467 19.6951 24.0336 20.3988 23.6208C21.1025 23.208 21.7457 22.7077 22.3284 22.12L26.2687 23.76L27.8209 21.04L24.398 18.44C24.5307 18.0667 24.6236 17.6736 24.6766 17.2608C24.7297 16.848 24.7562 16.4277 24.7562 16C24.7562 15.5723 24.7297 15.1525 24.6766 14.7408C24.6236 14.3291 24.5307 13.9355 24.398 13.56L27.8209 10.96L26.2687 8.24L22.3284 9.92C21.7446 9.30667 21.1014 8.7936 20.3988 8.3808C19.6962 7.968 18.9331 7.6544 18.1095 7.44L17.592 3.2H14.4478L13.8905 7.44C13.068 7.65333 12.3054 7.96693 11.6028 8.3808C10.9002 8.79467 10.2565 9.2944 9.67164 9.88L5.73134 8.24L4.1791 10.96L7.60199 13.52C7.46932 13.92 7.37645 14.32 7.32338 14.72C7.27032 15.12 7.24378 15.5467 7.24378 16C7.24378 16.4267 7.27032 16.84 7.32338 17.24C7.37645 17.64 7.46932 18.04 7.60199 18.44L4.1791 21.04L5.73134 23.76L9.67164 22.08C10.2554 22.6933 10.8991 23.2069 11.6028 23.6208C12.3065 24.0347 13.0691 24.3477 13.8905 24.56L14.408 28.8ZM16.0796 21.6C17.6186 21.6 18.932 21.0533 20.0199 19.96C21.1078 18.8667 21.6517 17.5467 21.6517 16C21.6517 14.4533 21.1078 13.1333 20.0199 12.04C18.932 10.9467 17.6186 10.4 16.0796 10.4C14.5141 10.4 13.1938 10.9467 12.1186 12.04C11.0435 13.1333 10.5064 14.4533 10.5075 16C10.5085 17.5467 11.0461 18.8667 12.1202 19.96C13.1943 21.0533 14.5141 21.6 16.0796 21.6Z" fill="black"/>
                </svg>
                Configuracion
              </div>
            </div>
          </button>

          <button href="#" style="margin-top: auto;" @click="emit('ir-a-bienvenida')">
            <div class="barra-dentro-cerrar w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 31 32" fill="none" style="flex-shrink: 0; width:1.3125rem; height:1.375rem;">
                  <path d="M3.44444 32C2.49722 32 1.68663 31.6521 1.01267 30.9564C0.338704 30.2607 0.00114815 29.4234 0 28.4444V3.55556C0 2.57778 0.337556 1.74104 1.01267 1.04533C1.68778 0.34963 2.49837 0.00118519 3.44444 0H15.5V3.55556H3.44444V28.4444H15.5V32H3.44444ZM22.3889 24.8889L20.0208 22.3111L24.4125 17.7778H10.3333V14.2222H24.4125L20.0208 9.68889L22.3889 7.11111L31 16L22.3889 24.8889Z" fill="#FF2A2A"/>
                </svg>
                Cerrar sesion
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <div class="titulo-pagina w-fit text-zinc-900 text-5xl font-semibold font-['Inter'] pb-2 mb-6 border-b-2 border-black">Notificaciones</div>

    <div class="contenido-pagina font-['Inter']">
      <div class="gap-6 flex flex-row">
        <button
          class="w-34 h-13 pb-0.5 rounded-[1.25rem] outline-[0.09375rem] outline-offset-[-0.09375rem] outline-black inline-flex justify-center items-center transition-colors"
          :class="filtro === 'todos' ? 'bg-zinc-200' : 'bg-white hover:bg-zinc-100'"
          @click="filtro = 'todos'"
        >
          <div class="text-center justify-center font-normal text-black text-[1rem] font-['Inter']">Todos</div>
        </button>
        <button
          class="w-34 h-13 pb-0.5 rounded-[1.25rem] outline-[0.09375rem] outline-offset-[-0.09375rem] outline-black inline-flex justify-center items-center transition-colors"
          :class="filtro === 'turnos' ? 'bg-zinc-200' : 'bg-white hover:bg-zinc-100'"
          @click="filtro = 'turnos'"
        >
          <div class="text-center justify-center text-black text-[1rem] font-normal font-['Inter']">Turnos</div>
        </button>
        <button
          class="w-34 h-13 pb-0.5 rounded-[1.25rem] outline-[0.09375rem] outline-offset-[-0.09375rem] outline-black inline-flex justify-center items-center transition-colors"
          :class="filtro === 'recordatorios' ? 'bg-zinc-200' : 'bg-white hover:bg-zinc-100'"
          @click="filtro = 'recordatorios'"
        >
          <div class="text-center justify-center text-black text-[1rem] font-normal font-['Inter']">Recordatorios</div>
        </button>
      </div>
      <p v-if="cargando" class="text-zinc-400 mt-10 text-2xl">Cargando notificaciones...</p>
      <p v-else-if="error" class="text-red-500 mt-10 text-2xl">{{ error }}</p>
      <p v-else-if="!notificacionesFiltradas.length" class="text-zinc-400 mt-10 text-2xl">No tenés notificaciones.</p>

      <div
        v-for="n in notificacionesFiltradas"
        :key="n.id"
        class="w-[84.6rem] h-20 flex items-center justify-between bg-white rounded-[2.5rem] shadow-[0rem_0rem_1.875rem_0.75rem_rgba(0,0,0,0.25)] mt-10 border border-sky-500"
      >
        <span class="ml-8 text-2xl font-normal font-['Inter']">{{ n.mensaje }}</span>
        <span class="mr-10 text-black/50 text-xl font-normal font-['Inter'] shrink-0">{{ formatearFecha(n.fecha) }}</span>
      </div>
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
