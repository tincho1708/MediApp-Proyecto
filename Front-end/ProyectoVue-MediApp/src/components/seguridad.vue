<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-chatbot',
  'ir-a-calendario',
  'ir-a-MediPlus',
  'ir-a-solicitudes',
  'ir-a-reservar-turno',
  'ir-a-mis-pacientes',
  'ir-a-configuracion',
  'ir-a-mi-usuario',
  'ir-a-seguridad',
])
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

function token() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  return sesion.token as string | undefined
}

const passwords = ref({ actual: '', nueva: '', confirmar: '' })
const campos: { clave: keyof typeof passwords.value; label: string; placeholder: string; completo?: boolean }[] = [
  { clave: 'actual', label: 'Contraseña actual', placeholder: '••••••••••••', completo: true },
  { clave: 'nueva', label: 'Nueva contraseña', placeholder: 'Ingresá una nueva contraseña' },
  { clave: 'confirmar', label: 'Confirmar nueva contraseña', placeholder: 'Repetí la nueva contraseña' },
]
const mensaje = ref('')
const error = ref(false)
const guardando = ref(false)

function mostrar(texto: string, esError: boolean) {
  mensaje.value = texto
  error.value = esError
}

function cancelarCambios() {
  passwords.value = { actual: '', nueva: '', confirmar: '' }
  mensaje.value = ''
}

async function actualizarPassword() {
  const { actual, nueva, confirmar } = passwords.value
  if (!actual || !nueva || !confirmar) return mostrar('Completá todos los campos.', true)
  if (nueva.length < 8) return mostrar('La nueva contraseña tiene que tener al menos 8 caracteres.', true)
  if (nueva !== confirmar) return mostrar('Las contraseñas nuevas no coinciden.', true)

  guardando.value = true
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/medicos/password`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
      body: JSON.stringify({ password_actual: actual, password_nueva: nueva }),
    })
    const data = await res.json()
    if (!res.ok) return mostrar(data.detail || 'No se pudo actualizar la contraseña.', true)
    passwords.value = { actual: '', nueva: '', confirmar: '' }
    mostrar(data.message, false)
  } catch {
    mostrar('No se pudo conectar con el servidor.', true)
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <div class="navbar">
    <button @click="emit('ir-a-principal')">
      <div class="navbar-logo" style="cursor: pointer">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
    </button>

    <div class="navbar-acciones">
      <button class="campoo" @click="emit('ir-a-chatbot')">MediBot<span class="campoo-indicador"></span></button>
      <button class="campoo" @click="emit('ir-a-mis-pacientes')">Mis pacientes<span class="campoo-indicador"></span></button>
      <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes<span class="campoo-indicador"></span></button>
      <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+<span class="campoo-indicador"></span></button>
    </div>

    <div class="navbar-usuario-zona">
      <div class="navbar-divisor"></div>
      <button class="navbar-usuario" @click.stop="esta = !esta">
        <Avatar propia class="navbar-usuario-avatar" :texto="nombreUsuario.charAt(0).toUpperCase()" />
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
          <div class="dropdown-rol">Cuenta de médico</div>
        </div>
        <div class="dropdown-divisor"></div>


        <button @click="emit('ir-a-mi-usuario')">
          <div class="dropdown-item dropdown-item-destacado">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            Configuración
          </div>
        </button>

        <button @click="emit('ir-a-bienvenida')">
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

  <div class="min-h-screen lg:h-screen lg:overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
    <div class="flex-1 min-h-0 px-4 sm:px-16 pt-6 pb-6 flex flex-col gap-5">
      <div class="shrink-0">
        <h1 class="text-3xl font-semibold text-[#182234]">Configuración</h1>
        <p class="text-sm text-[#61718B] mt-1">Administrá tu cuenta y la disponibilidad de tu consultorio.</p>
      </div>

      <div class="lg:flex-1 lg:min-h-0 flex flex-col lg:flex-row gap-6">
        <nav class="lg:w-60 shrink-0 p-5 bg-white rounded-2xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11)] flex flex-col gap-2 text-sm text-[#182234]">
          <button class="h-12 px-3 rounded-xl flex items-center gap-3 text-left cursor-pointer hover:bg-[#F4F7FB]" @click="emit('ir-a-mi-usuario')">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></svg>
            Mi usuario
          </button>
          <div class="h-12 px-3 rounded-xl flex items-center gap-3 bg-[#EDF5FF] font-semibold text-[#3D6FC2]">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" /></svg>
            Seguridad
          </div>
          <div class="h-12 px-3 rounded-xl flex items-center gap-3">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
            Preferencias
          </div>
          <button class="h-12 px-3 rounded-xl flex items-center gap-3 text-left cursor-pointer hover:bg-[#F4F7FB]" @click="emit('ir-a-configuracion')">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
            Disponibilidad
          </button>

          <div class="mt-auto pt-2 border-t border-[#D7E2F0]">
            <button class="w-full h-11 px-3 flex items-center gap-3 text-[#BE185D] cursor-pointer" @click="emit('ir-a-bienvenida')">
              <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
              Cerrar sesión
            </button>
          </div>
        </nav>

        <section class="flex-1 min-w-0 min-h-0 p-6 bg-white rounded-2xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11)] flex flex-col gap-4">
          <div class="shrink-0">
            <h2 class="text-2xl font-semibold text-[#182234]">Seguridad</h2>
            <p class="text-sm text-[#61718B] mt-1">Actualizá tu contraseña y revisá el acceso a tu cuenta.</p>
          </div>
          <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

          <div class="lg:flex-1 lg:min-h-0 lg:overflow-y-auto flex flex-col gap-4">
            <h3 class="text-lg font-semibold text-[#182234]">Cambiar contraseña</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <label v-for="campo in campos" :key="campo.clave" class="flex flex-col gap-2" :class="{ 'sm:col-span-2': campo.completo }">
                <span class="text-xs text-[#61718B]">{{ campo.label }}</span>
                <input v-model="passwords[campo.clave]" type="password" :placeholder="campo.placeholder" class="h-12 px-4 bg-[#F4F7FB] rounded-xl outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234] placeholder:text-[#182234] focus:outline-[#3D6FC2]" />
              </label>
            </div>
            <p class="text-xs text-[#61718B]">Usá al menos 8 caracteres y combiná letras, números y símbolos.</p>
          </div>

          <div class="shrink-0 mt-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span class="text-xs" :class="!mensaje ? 'text-[#61718B]' : error ? 'text-red-600' : 'text-green-600'">{{ mensaje || 'Los cambios se aplican al guardar.' }}</span>
            <div class="flex gap-3">
              <button class="w-32 h-11 px-4 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="cancelarCambios">Cancelar</button>
              <button class="w-60 h-11 px-4 bg-[#3D6FC2] rounded-xl text-base font-medium text-white cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-50" :disabled="guardando" @click="actualizarPassword">{{ guardando ? 'Guardando...' : 'Guardar cambios' }}</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
