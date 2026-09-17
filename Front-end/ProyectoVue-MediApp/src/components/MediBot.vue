<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-principal-usuario',
  'ir-a-solicitudes',
  'ir-a-MediPlus',
  'ir-a-calendario',
  'ir-a-calendario-usuario',
  'ir-a-reservar-turno',
])

/* ---------------- sesión ---------------- */

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const token = sesion.token as string | undefined
const esMedico = sesion.tipo === 'Medico'

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

/* ---------------- menú lateral ---------------- */

const esta = ref(false)
function cerrarAlClickFuera() { esta.value = false }
onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

/* ---------------- chat ---------------- */

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
const panelAbierto = ref(false)
const cargandoPanel = ref(false)

const scroller = ref<HTMLElement | null>(null)
const caja = ref<HTMLTextAreaElement | null>(null)

const vacio = computed(() => mensajes.value.length === 0)

const sugerencias = computed(() =>
  esMedico
    ? ['¿Cómo viene mi semana?', '¿Cuántos pacientes tengo?', '¿Tengo solicitudes sin responder?']
    : ['Necesito un psicólogo', '¿Qué especialidades hay?', '¿Cuándo es mi próximo turno?'],
)

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
  } catch (e) {
    // Sacamos el mensaje para que lo pueda reintentar sin que quede duplicado.
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

/* ---------------- historial ---------------- */

async function togglePanel() {
  panelAbierto.value = !panelAbierto.value
  if (!panelAbierto.value) return

  cargandoPanel.value = true
  try {
    const res = await fetch(`${API}/medibot/conversaciones`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    conversaciones.value = res.ok ? await res.json() : []
  } catch {
    conversaciones.value = []
  } finally {
    cargandoPanel.value = false
  }
}

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
    panelAbierto.value = false
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
    conversaciones.value = conversaciones.value.filter(c => c.id !== id)
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

/* Formato mínimo: **negrita**, viñetas y saltos de línea.
   Se escapa el HTML primero para que no se pueda inyectar nada en la página. */
function formatear(texto: string) {
  const escapado = texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escapado
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^[-*]\s+/gm, '• ')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <div class="navbar">
    <button @click="emit(esMedico ? 'ir-a-principal' : 'ir-a-principal-usuario')">
      <div class="navbar-logo" style="cursor:pointer">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
    </button>

    <div class="navbar-acciones">
      <template v-if="esMedico">
        <button class="campoo campoo-activo">MediBot</button>
        <button class="campoo" @click="emit('ir-a-calendario')">Mis pacientes</button>
        <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes</button>
        <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+</button>
      </template>
      <template v-else>
        <button class="campoo" @click="emit('ir-a-reservar-turno')">Reservar Turno</button>
        <button class="campoo campoo-activo">MediBot</button>
        <button class="campoo" @click="emit('ir-a-calendario-usuario')">Mis turnos</button>
      </template>

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

  <!-- ===================== CHAT ===================== -->

  <div class="chat">
    <div ref="scroller" class="chat-scroll">
      <div class="chat-ancho">

        <!-- Pantalla inicial -->
        <div v-if="vacio" class="inicio">
          <h1 class="titulo">Preguntale algo a <span>MediBot</span></h1>
          <p class="subtitulo">
            {{ esMedico
              ? 'Puedo mirar tu agenda, tus pacientes y las solicitudes que tenés sin responder.'
              : 'Puedo buscarte profesionales, contarte sobre ellos y mostrarte tus turnos.' }}
          </p>
          <div class="sugerencias">
            <button v-for="s in sugerencias" :key="s" class="sugerencia" @click="enviar(s)">
              {{ s }}
            </button>
          </div>
        </div>

        <!-- Mensajes -->
        <div v-else class="mensajes">
          <div v-for="(m, i) in mensajes" :key="i">
            <div v-if="m.role === 'user'" class="fila-usuario">
              <p class="burbuja-usuario">{{ m.content }}</p>
            </div>
            <div v-else class="fila-bot">
              <img class="avatar-bot" src="@/assets/imagenes/imagen-logo.png" alt="MediBot" />
              <div class="texto-bot" v-html="formatear(m.content)"></div>
            </div>
          </div>

          <div v-if="pensando" class="fila-bot">
            <img class="avatar-bot" src="@/assets/imagenes/imagen-logo.png" alt="MediBot" />
            <div class="puntitos" aria-label="MediBot está escribiendo">
              <i></i><i></i><i></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Barra de escritura -->
    <div class="pie">
      <p v-if="error" class="error">{{ error }}</p>

      <div class="barra-mensaje">
        <div class="barra-mensaje-avatar">
          <img src="@/assets/imagenes/imagen-logo.png" alt="MediBot" />
        </div>
        <textarea
          ref="caja"
          v-model="borrador"
          rows="1"
          placeholder="Escribe algo..."
          :disabled="ocupado"
          maxlength="4000"
          @input="ajustarAltura"
          @keydown="teclado"
        ></textarea>
        <button class="enviar" :disabled="!borrador.trim() || ocupado" @click="enviar()" aria-label="Enviar mensaje">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 4l7 7h-5v9h-4v-9H5z" />
          </svg>
        </button>
      </div>

      <div class="acciones-pie">
        <button class="link" @click="togglePanel">Ver chats anteriores</button>
        <button v-if="!vacio" class="link" :disabled="ocupado" @click="nuevaConversacion">Empezar de nuevo</button>
      </div>
    </div>

    <!-- Historial -->
    <aside :class="['panel', { 'panel-abierto': panelAbierto }]">
      <header class="panel-header">
        <h2>Chats anteriores</h2>
        <button class="cerrar-panel" @click="panelAbierto = false" aria-label="Cerrar">✕</button>
      </header>
      <div class="panel-lista">
        <p v-if="cargandoPanel" class="panel-vacio">Cargando...</p>
        <p v-else-if="!conversaciones.length" class="panel-vacio">
          Todavía no hablaste con MediBot. Cuando lo hagas, tus conversaciones van a aparecer acá.
        </p>
        <div v-for="c in conversaciones" :key="c.id" class="panel-item">
          <button class="panel-item-abrir" :disabled="ocupado" @click="abrirConversacion(c.id)">
            <span class="panel-item-titulo">{{ c.titulo }}</span>
            <span class="panel-item-fecha">{{ fechaCorta(c.creado_en) }}</span>
          </button>
          <button class="panel-item-borrar" :disabled="ocupado" @click="borrarConversacion(c.id)" aria-label="Borrar conversación">✕</button>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.chat {
  position: fixed;
  inset: 5.4rem 0 0 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #BCD9F7 0%, #E6F1FC 55%, #FFFFFF 100%);
}

.chat-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem;
}

.chat-ancho {
  max-width: 48rem;
  margin: 0 auto;
  width: 100%;
  min-height: 100%;
}

/* ---------- pantalla inicial ---------- */

.inicio {
  padding-top: 5rem;
  text-align: center;
}

.titulo {
  font-family: 'Inter', sans-serif;
  font-size: 3rem;
  font-weight: 400;
  color: #1C1C1C;
  line-height: 1.15;
}

.titulo span { color: #2F97E0; }

.subtitulo {
  margin-top: 1rem;
  font-size: 1.05rem;
  color: #3A4A5C;
}

.sugerencias {
  margin-top: 2.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
}

.sugerencia {
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(47, 151, 224, 0.3);
  border-radius: 9999px;
  padding: 0.6rem 1.1rem;
  font-size: 0.95rem;
  color: #2440A8;
  cursor: pointer;
  transition: background 0.2s ease;
}

.sugerencia:hover { background: #fff; }

/* ---------- mensajes ---------- */

.mensajes {
  padding: 2rem 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.fila-usuario { display: flex; justify-content: flex-end; }

.burbuja-usuario {
  max-width: 80%;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 1.5rem;
  padding: 0.75rem 1.25rem;
  color: #1C1C1C;
  white-space: pre-wrap;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.fila-bot { display: flex; gap: 0.75rem; align-items: flex-start; }

.avatar-bot {
  width: 2rem;
  height: 2rem;
  object-fit: contain;
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.texto-bot {
  max-width: 85%;
  color: #1C1C1C;
  line-height: 1.6;
}

.puntitos { display: flex; gap: 0.35rem; padding-top: 0.6rem; }

.puntitos i {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: #2F97E0;
  animation: latir 1.2s infinite ease-in-out;
}

.puntitos i:nth-child(2) { animation-delay: 0.15s; }
.puntitos i:nth-child(3) { animation-delay: 0.3s; }

@keyframes latir {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .puntitos i { animation: none; opacity: 0.6; }
}

/* ---------- pie ---------- */

.pie { padding: 0 1.5rem 1.5rem; }

.error {
  max-width: 48rem;
  margin: 0 auto 0.75rem;
  text-align: center;
  color: #B42318;
  font-size: 0.9rem;
}

.barra-mensaje {
  max-width: 48rem;
  margin: 0 auto;
  min-height: 4.5rem;
  background: #fff;
  border-radius: 2rem;
  box-shadow: 0 8px 28px rgba(36, 64, 168, 0.18);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
}

.barra-mensaje-avatar {
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.barra-mensaje-avatar img { width: 100%; height: 100%; object-fit: contain; }

.barra-mensaje textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  max-height: 8.75rem;
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  color: #000;
  background: transparent;
  line-height: 1.5;
}

.barra-mensaje textarea::placeholder { color: #9ca3af; }

.enviar {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  border: none;
  border-radius: 9999px;
  background: #2440A8;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.enviar:hover:not(:disabled) { background: #1c3488; }
.enviar:disabled { background: #D1D5DB; cursor: default; }

.acciones-pie {
  margin-top: 0.85rem;
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.link {
  background: none;
  border: none;
  font-size: 0.95rem;
  color: #1C1C1C;
  cursor: pointer;
}

.link:hover { text-decoration: underline; }

/* ---------- panel de historial ---------- */

.panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 20rem;
  max-width: 85vw;
  background: #fff;
  box-shadow: -0.5rem 0 1.5rem rgba(36, 64, 168, 0.2);
  transform: translateX(100%);
  transition: transform 0.25s ease;
  display: flex;
  flex-direction: column;
  z-index: 20;
}

.panel-abierto { transform: translateX(0); }

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid #E5E7EB;
}

.panel-header h2 { font-size: 1.1rem; font-weight: 500; color: #1C1C1C; }

.cerrar-panel {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #6B7280;
  cursor: pointer;
}

.panel-lista { flex: 1; overflow-y: auto; padding: 0.75rem; }

.panel-vacio { padding: 1.5rem 0.75rem; font-size: 0.9rem; color: #6B7280; }

.panel-item { display: flex; align-items: center; gap: 0.25rem; }

.panel-item-abrir {
  flex: 1;
  text-align: left;
  background: none;
  border: none;
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  overflow: hidden;
}

.panel-item-abrir:hover { background: #E6F1FC; }

.panel-item-titulo {
  display: block;
  font-size: 0.9rem;
  color: #1C1C1C;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.panel-item-fecha { font-size: 0.75rem; color: #6B7280; }

.panel-item-borrar {
  background: none;
  border: none;
  color: #9CA3AF;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 0.5rem;
}

.panel-item-borrar:hover { color: #B42318; background: #FEF2F2; }

/* ---------- navbar ---------- */

.campoo-activo { background-color: #C6E9FF; }

@media (max-width: 768px) {
  .titulo { font-size: 2rem; }
  .barra-mensaje textarea { font-size: 1rem; }
  .inicio { padding-top: 2.5rem; }
}
</style>
