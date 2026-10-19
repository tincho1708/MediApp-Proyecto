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
const nombreUsuario = sesion.nombre || 'Usuario'
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
        <button class="campoo" @click="emit('ir-a-reservar-turno')">Reservar turno<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot<span class="campoo-indicador"></span></button>
        <button class="campoo">Profesionales<span class="campoo-indicador"></span></button>
        <button class="campoo activo">Notificaciones<span class="campoo-indicador"></span></button>
      </div>

      <div class="navbar-usuario-zona">
        <div class="navbar-divisor"></div>
        <button class="navbar-usuario" @click.stop="esta = !esta">
          <div class="navbar-usuario-avatar">{{ nombreUsuario.charAt(0).toUpperCase() }}</div>
          <div class="navbar-usuario-info">
            <span class="navbar-usuario-nombre">{{ nombreUsuario }}</span>
            <span class="navbar-usuario-rol">Mi cuenta</span>
          </div>
          <svg style="width:1rem; height:1rem;" class="navbar-usuario-chevron" :class="{ 'navbar-usuario-chevron-abierta': esta }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
        </button>

        <div :class="['barra-desplegable', { 'barra-abierta': esta }]" @click.stop>
          <div class="dropdown-header">
            <div class="dropdown-nombre">{{ nombreUsuario }}</div>
            <div class="dropdown-rol">Cuenta de paciente</div>
          </div>
          <div class="dropdown-divisor"></div>

          <button href="#" @click="emit('ir-a-mi-usuario-paciente')">
            <div class="dropdown-item dropdown-item-destacado">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              Configuración
            </div>
          </button>

          <button href="#" @click="emit('ir-a-bienvenida')">
            <div class="dropdown-item dropdown-item-danger">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>
              </svg>
              Cerrar sesión
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
