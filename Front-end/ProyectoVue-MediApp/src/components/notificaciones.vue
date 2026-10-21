<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-calendario-usuario', 'ir-a-reservar-turno', 'ir-a-mi-usuario-paciente', 'ir-a-notificaciones'])
const { resetConteoNoLeidas } = useConteoNoLeidas()

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
  resetConteoNoLeidas()
}

onMounted(cargarNotificaciones)

const filtro = ref<'todos' | 'turnos' | 'recordatorios'>('todos')

const notificacionesFiltradas = computed(() => {
  if (filtro.value === 'turnos') return notificaciones.value
  if (filtro.value === 'recordatorios') return []
  return notificaciones.value
})

function formatearHora(fecha: string) {
  const f = new Date(fecha)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}

function formatearFechaCorta(fecha: string) {
  const f = new Date(fecha)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getDate())}/${pad(f.getMonth() + 1)}/${f.getFullYear()}`
}

const nombresMes = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

function formatearFechaGrupo(fecha: string) {
  const f = new Date(fecha)
  return `${f.getDate()} de ${nombresMes[f.getMonth()]} de ${f.getFullYear()}`
}

function tituloNotificacion(n: NotificacionPaciente) {
  if (n.mensaje.includes('rechazado')) return 'Solicitud rechazada'
  if (n.mensaje.includes('aceptado')) return 'Solicitud aceptada'
  return 'Notificación'
}

function esAceptada(n: NotificacionPaciente) {
  return n.mensaje.includes('aceptado')
}

const gruposNotificaciones = computed(() => {
  const mapa = new Map<string, NotificacionPaciente[]>()
  for (const n of notificacionesFiltradas.value) {
    const clave = formatearFechaGrupo(n.fecha)
    if (!mapa.has(clave)) mapa.set(clave, [])
    mapa.get(clave)!.push(n)
  }
  return [...mapa.entries()].map(([fecha, items]) => ({ fecha, items }))
})
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

    <div class="h-screen overflow-hidden bg-linear-to-br from-blue-100 via-violet-100 to-blue-200 pt-[4.9rem] flex flex-col font-['Inter']">
      <div class="flex items-start justify-between max-w-[82rem] w-full mx-auto px-16 pt-10 pb-6 shrink-0">
        <div>
          <div class="text-3xl font-semibold text-slate-900">Notificaciones</div>
          <p class="text-sm text-slate-500 mt-1.5">Mantenete al día con tus turnos y recordatorios.</p>
        </div>
        <button
          class="flex items-center gap-2 h-11 px-4 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-xl text-sm font-medium text-sky-700 cursor-pointer hover:bg-slate-50 transition-colors"
          @click="marcarTodasComoLeidas"
        >
          <svg style="width:1rem; height:1rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
          Marcar todas como leídas
        </button>
      </div>

      <div class="flex-1 min-h-0 max-w-[82rem] w-full mx-auto px-16 pb-10">
        <div class="h-full bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-6 flex flex-col gap-6 min-h-0">
          <div class="flex items-center gap-3 shrink-0">
            <button
              class="h-11 px-5 rounded-xl text-sm font-medium cursor-pointer transition-colors"
              :class="filtro === 'todos' ? 'bg-blue-50 text-sky-700' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 hover:bg-slate-50'"
              @click="filtro = 'todos'"
            >Todas</button>
            <button
              class="h-11 px-5 rounded-xl text-sm font-medium cursor-pointer transition-colors"
              :class="filtro === 'turnos' ? 'bg-blue-50 text-sky-700' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 hover:bg-slate-50'"
              @click="filtro = 'turnos'"
            >Turnos</button>
            <button
              class="h-11 px-5 rounded-xl text-sm font-medium cursor-pointer transition-colors"
              :class="filtro === 'recordatorios' ? 'bg-blue-50 text-sky-700' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-sky-700 hover:bg-slate-50'"
              @click="filtro = 'recordatorios'"
            >Recordatorios</button>
            <div class="flex-1"></div>
            <span class="text-xs text-slate-400 whitespace-nowrap">{{ notificacionesFiltradas.length }} notificacion{{ notificacionesFiltradas.length !== 1 ? 'es' : '' }}</span>
          </div>

          <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-6">
            <p v-if="cargando" class="text-slate-400 text-sm">Cargando notificaciones...</p>
            <p v-else-if="error" class="text-red-600 text-sm">{{ error }}</p>
            <p v-else-if="!notificacionesFiltradas.length" class="text-slate-400 text-sm text-center py-6">No tenés notificaciones.</p>

            <div v-else v-for="grupo in gruposNotificaciones" :key="grupo.fecha" class="flex flex-col gap-3 shrink-0">
              <div class="text-sm font-medium text-slate-500">{{ grupo.fecha }}</div>

              <div
                v-for="n in grupo.items" :key="n.id"
                class="flex items-start gap-5 p-6 bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-2xl"
              >
                <div class="size-11 shrink-0 rounded-xl bg-blue-50 flex items-center justify-center">
                  <svg style="width:1.25rem; height:1.25rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-sky-700"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></svg>
                </div>
                <div class="flex-1 min-w-0 flex flex-col gap-2">
                  <div class="text-lg font-semibold text-slate-900">{{ tituloNotificacion(n) }}</div>
                  <div class="text-sm text-slate-500">{{ n.mensaje }}</div>
                  <button v-if="esAceptada(n)" class="text-sm font-medium text-sky-700 text-left cursor-pointer hover:underline" @click="emit('ir-a-calendario-usuario')">Ver en mi calendario →</button>
                </div>
                <div class="flex flex-col items-end gap-2 shrink-0">
                  <span class="text-sm font-medium text-slate-500">{{ formatearHora(n.fecha) }}</span>
                  <span class="text-xs text-slate-400">{{ formatearFechaCorta(n.fecha) }}</span>
                </div>
              </div>
            </div>

            <p v-if="!cargando && !error && notificacionesFiltradas.length" class="text-sm text-slate-400 text-center shrink-0">No tenés más notificaciones.</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
</style>
