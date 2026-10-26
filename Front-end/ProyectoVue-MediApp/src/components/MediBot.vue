<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits([
  'ir-a-profesionales',
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-principal-usuario',
  'ir-a-solicitudes',
  'ir-a-MediPlus',
  'ir-a-calendario',
  'ir-a-calendario-usuario',
  'ir-a-reservar-turno',
  'ir-a-mis-pacientes',
  'ir-a-configuracion',
  'ir-a-notificaciones',
  'ir-a-mi-usuario-paciente',
])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const token = sesion.token as string | undefined
const esMedico = sesion.tipo === 'Medico'
const nombreUsuario = sesion.nombre || 'Usuario'

const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

const esta = ref(false)
function cerrarAlClickFuera() {
  esta.value = false
}
onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

type Mensaje = { role: 'user' | 'assistant'; content: string }
type Conversacion = { id: number; titulo: string; creado_en: string }

const mensajes = ref<Mensaje[]>([])
const borrador = ref('')
const pensando = ref(false)
const cargandoConversacion = ref(false)
const ocupado = computed(() => pensando.value || cargandoConversacion.value)
const error = ref('')
const conversacionId = ref<number | null>(null)

const conversaciones = ref<Conversacion[]>([])
const cargandoConversaciones = ref(false)

const scroller = ref<HTMLElement | null>(null)
const caja = ref<HTMLTextAreaElement | null>(null)

const vacio = computed(() => mensajes.value.length === 0)

type Sugerencia = { titulo: string; desc: string }

const sugerencias = computed<Sugerencia[]>(() =>
  esMedico
    ? [
        { titulo: 'Mi semana', desc: '¿Cómo viene mi semana?' },
        { titulo: 'Mis pacientes', desc: '¿Cuántos pacientes tengo?' },
        { titulo: 'Solicitudes pendientes', desc: '¿Tengo solicitudes sin responder?' },
      ]
    : [
        {
          titulo: 'Encontrar un profesional',
          desc: '¿Cómo busco un profesional por especialidad?',
        },
        {
          titulo: 'Preparar mi consulta',
          desc: 'Ayudame a ordenar mis preguntas para la consulta.',
        },
        { titulo: 'Usar MediApp', desc: '¿Cómo consulto o modifico mis próximos turnos?' },
      ],
)

const tituloConversacion = computed(() => {
  if (conversacionId.value === null) return 'Nueva conversación'
  return conversaciones.value.find((c) => c.id === conversacionId.value)?.titulo || 'Conversación'
})

async function bajarScroll() {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

function ajustarAltura() {
  const el = caja.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

async function enviar(texto?: string) {
  const contenido = (texto ?? borrador.value).trim()
  if (!contenido || ocupado.value) return
  if (!token) {
    error.value = 'Iniciá sesión para usar MediBot.'
    return
  }
  if (contenido.length > 4000) {
    error.value = 'El mensaje puede tener hasta 4000 caracteres.'
    return
  }

  error.value = ''
  mensajes.value.push({ role: 'user', content: contenido })
  borrador.value = ''
  nextTick(ajustarAltura)
  pensando.value = true
  bajarScroll()

  try {
    const res = await fetch(`${API}/medibot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        messages: [{ role: 'user', content: contenido }],
        conversacion_id: conversacionId.value,
      }),
    })

    if (res.status === 401) throw new Error('Tu sesión venció. Volvé a iniciar sesión.')
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || 'MediBot no pudo responder.')
    }

    const data = await res.json()
    conversacionId.value = data.conversacion_id
    mensajes.value.push({ role: 'assistant', content: data.respuesta })
    cargarConversaciones()
  } catch (e) {
    mensajes.value.pop()
    borrador.value = contenido
    error.value = e instanceof Error ? e.message : 'No se pudo conectar con MediBot.'
  } finally {
    pensando.value = false
    bajarScroll()
  }
}

function teclado(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    enviar()
  }
}

async function cargarConversaciones() {
  if (!token) return
  cargandoConversaciones.value = true
  try {
    const res = await fetch(`${API}/medibot/conversaciones`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    conversaciones.value = res.ok ? await res.json() : []
  } catch {
    conversaciones.value = []
  } finally {
    cargandoConversaciones.value = false
  }
}

onMounted(cargarConversaciones)

async function abrirConversacion(id: number) {
  if (ocupado.value) return
  cargandoConversacion.value = true
  try {
    const res = await fetch(`${API}/medibot/conversaciones/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('No se pudo abrir esa conversación.')
    const data = await res.json()
    mensajes.value = data.map((m: { rol: string; contenido: string }) => ({
      role: m.rol as 'user' | 'assistant',
      content: m.contenido,
    }))
    conversacionId.value = id
    bajarScroll()
  } catch {
    error.value = 'No se pudo abrir esa conversación.'
  } finally {
    cargandoConversacion.value = false
  }
}

async function borrarConversacion(id: number) {
  if (ocupado.value) return
  cargandoConversacion.value = true
  try {
    const res = await fetch(`${API}/medibot/conversaciones/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('No se pudo borrar esa conversación.')
    conversaciones.value = conversaciones.value.filter((c) => c.id !== id)
    if (conversacionId.value === id) {
      mensajes.value = []
      conversacionId.value = null
    }
  } catch {
    error.value = 'No se pudo borrar esa conversación.'
  } finally {
    cargandoConversacion.value = false
  }
}

function nuevaConversacion() {
  if (ocupado.value) return
  mensajes.value = []
  conversacionId.value = null
  error.value = ''
}

function fechaCorta(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function formatear(texto: string) {
  const escapado = texto.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return escapado
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^[-*]\s+/gm, '• ')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <div class="navbar">
    <button @click="emit(esMedico ? 'ir-a-principal' : 'ir-a-principal-usuario')">
      <div class="navbar-logo" style="cursor: pointer">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
    </button>

    <div class="navbar-acciones">
      <template v-if="esMedico">
        <button class="campoo activo">MediBot<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-mis-pacientes')">
          Mis pacientes<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-solicitudes')">
          Solicitudes<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-MediPlus')">
          MediApp+<span class="campoo-indicador"></span>
        </button>
      </template>
      <template v-else>
        <button class="campoo" @click="emit('ir-a-reservar-turno')">
          Reservar turno<span class="campoo-indicador"></span>
        </button>
        <button class="campoo activo">MediBot<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-profesionales')">
          Profesionales<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-notificaciones')">
          Notificaciones<span v-if="conteoNoLeidas > 0" class="campoo-punto"></span
          ><span class="campoo-indicador"></span>
        </button>
      </template>
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
          <div class="dropdown-rol">{{ esMedico ? 'Cuenta de médico' : 'Cuenta de paciente' }}</div>
        </div>
        <div class="dropdown-divisor"></div>


        <button href="#" @click="emit(esMedico ? 'ir-a-configuracion' : 'ir-a-mi-usuario-paciente')">
          <div class="dropdown-item dropdown-item-destacado">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            Configuración
          </div>
        </button>

        <button href="#" @click="emit('ir-a-bienvenida')">
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

  <div class="h-screen overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
    <div class="flex-1 min-h-0 max-w-328 w-full mx-auto px-16 py-10 flex flex-col gap-8">
      <div class="shrink-0">
        <div class="text-3xl font-semibold text-slate-900">MediBot</div>
        <p class="text-sm text-slate-500 mt-1">
          Tu asistente para orientarte en MediApp y preparar tus consultas.
        </p>
      </div>

      <div class="flex-1 min-h-0 flex gap-6">
        <div class="w-72 shrink-0 bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-6 flex flex-col gap-6 min-h-0">
          <button class="shrink-0 h-11 bg-[#3D6FC2] text-white rounded-xl flex items-center justify-center gap-2 text-sm font-medium cursor-pointer hover:opacity-90 transition-opacity" :disabled="ocupado" @click="nuevaConversacion">
            <svg style="width: 1rem; height: 1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Nueva conversación
          </button>

          <div class="text-xs font-medium text-slate-400 tracking-wide shrink-0">
            CONVERSACIONES
          </div>

          <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-1.5">
            <p v-if="cargandoConversaciones" class="text-sm text-slate-400 text-center py-4">
              Cargando...
            </p>

            <div v-else-if="!conversaciones.length" class="bg-slate-50 rounded-2xl p-4 flex flex-col items-center text-center gap-2">
              <svg style="width: 1.5rem; height: 1.5rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <div class="text-sm font-medium text-slate-900">Sin conversaciones todavía</div>
              <div class="text-xs text-slate-400">
                Cuando inicies un chat, aparecerá en este espacio.
              </div>
            </div>

            <div v-else v-for="c in conversaciones" :key="c.id" class="group flex items-center gap-1 shrink-0">
              <button class="flex-1 min-w-0 text-left rounded-xl px-3 py-2.5 transition-colors cursor-pointer" :class="conversacionId === c.id ? 'bg-blue-50' : 'hover:bg-slate-50'" :disabled="ocupado" @click="abrirConversacion(c.id)">
                <div class="text-sm font-medium text-slate-900 truncate">{{ c.titulo }}</div>
                <div class="text-xs text-slate-400">{{ fechaCorta(c.creado_en) }}</div>
              </button>
              <button class="shrink-0 p-2 rounded-lg text-slate-300 opacity-0 group-hover:opacity-100 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer" :disabled="ocupado" @click="borrarConversacion(c.id)" aria-label="Borrar conversación">
                <svg style="width: 0.875rem; height: 0.875rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="flex-1 min-h-0 bg-white rounded-3xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)] outline-1 -outline-offset-1 outline-slate-200 p-6 flex flex-col gap-4 min-h-0">
          <div class="flex items-center gap-2 shrink-0">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" class="text-[#3D6FC2]">
              <path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8" />
            </svg>
            <span class="text-sm font-medium text-slate-900">{{ tituloConversacion }}</span>
            <div class="flex-1"></div>
            <span class="text-xs text-slate-400 whitespace-nowrap">MediBot · IA</span>
          </div>

          <div ref="scroller" class="flex-1 min-h-0 overflow-y-auto">
            <div v-if="vacio" class="h-full flex flex-col items-center justify-center gap-6 text-center px-4">
              <div class="size-16 bg-blue-50 rounded-3xl flex items-center justify-center shrink-0">
                <svg style="width: 2rem; height: 2rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" class="text-[#3D6FC2]">
                  <path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8" />
                </svg>
              </div>
              <div class="flex flex-col items-center gap-2 max-w-[54rem]">
                <h1 class="text-3xl font-semibold text-slate-900">¿En qué puedo ayudarte hoy?</h1>
                <p class="text-sm text-slate-500">
                  Escribí tu consulta o elegí una sugerencia para empezar.
                </p>
              </div>
              <div class="flex gap-3 w-full max-w-[54rem]">
                <button v-for="s in sugerencias" :key="s.titulo" class="flex-1 min-w-0 p-3 bg-slate-50 rounded-2xl outline-1 -outline-offset-1 outline-slate-200 text-left cursor-pointer hover:bg-slate-100 transition-colors" @click="enviar(s.desc)">
                  <div class="text-sm font-medium text-[#3D6FC2] truncate">{{ s.titulo }}</div>
                  <div class="text-xs text-slate-400 mt-1 line-clamp-2">{{ s.desc }}</div>
                </button>
              </div>
            </div>

            <div v-else class="flex flex-col gap-6 py-2">
              <div v-for="(m, i) in mensajes" :key="i">
                <div v-if="m.role === 'user'" class="flex justify-end">
                  <p class="max-w-[80%] bg-blue-50 rounded-2xl px-5 py-3 text-sm text-slate-900 whitespace-pre-wrap">
                    {{ m.content }}
                  </p>
                </div>
                <div v-else class="flex gap-3 items-start">
                  <img class="w-8 h-8 object-contain shrink-0 mt-0.5" src="@/assets/imagenes/imagen-logo.png" alt="MediBot" />
                  <div class="max-w-[85%] text-sm text-slate-900 leading-relaxed mediBotTexto" v-html="formatear(m.content)"></div>
                </div>
              </div>

              <div v-if="pensando" class="flex gap-3 items-start">
                <img class="w-8 h-8 object-contain shrink-0 mt-0.5" src="@/assets/imagenes/imagen-logo.png" alt="MediBot" />
                <div class="flex gap-1.5 pt-2" aria-label="MediBot está escribiendo">
                  <i class="puntito"></i><i class="puntito"></i><i class="puntito"></i>
                </div>
              </div>
            </div>
          </div>

          <div class="shrink-0">
            <p v-if="error" class="text-red-600 text-sm mb-2">{{ error }}</p>
            <div class="bg-white outline-1 -outline-offset-1 outline-slate-200 rounded-2xl p-4 flex flex-col gap-3">
              <textarea ref="caja" v-model="borrador" rows="1" placeholder="Escribí tu consulta a MediBot…" :disabled="ocupado" maxlength="4000" class="w-full border-none outline-none resize-none text-sm text-slate-900 placeholder:text-slate-400 bg-transparent" style="max-height: 8.75rem" @input="ajustarAltura" @keydown="teclado"></textarea>
              <div class="flex items-center justify-between">
                <span class="text-xs text-slate-400">Una conversación, a tu ritmo.</span>
                <button class="size-10 shrink-0 bg-[#3D6FC2] rounded-xl flex items-center justify-center text-white hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer" :disabled="!borrador.trim() || ocupado" @click="enviar()" aria-label="Enviar mensaje">
                  <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 19V5M5 12l7-7 7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.puntito {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
  background: #3d6fc2;
  animation: latir 1.2s infinite ease-in-out;
}

.puntito:nth-child(2) {
  animation-delay: 0.15s;
}
.puntito:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes latir {
  0%,
  60%,
  100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .puntito {
    animation: none;
    opacity: 0.6;
  }
}

.mediBotTexto :deep(strong) {
  font-weight: 600;
}
</style>
