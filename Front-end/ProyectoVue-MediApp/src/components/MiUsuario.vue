<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { actualizarSesion, subirFoto } from '@/fotoPerfil'

const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-chatbot',
  'ir-a-calendario',
  'ir-a-MediPlus',
  'ir-a-solicitudes',
  'ir-a-mis-pacientes',
  'ir-a-configuracion',
  'ir-a-seguridad',
  'ir-a-mi-usuario',
])

const API = import.meta.env.VITE_API_URL
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = ref(sesion.nombre || 'Usuario')
const headers = { Authorization: `Bearer ${sesion.token}`, 'Content-Type': 'application/json' }

const vacio = { nombre: '', apellido: '', mail: '', telefono: '', dni: '', fecha_nacimiento: '' }
const guardado = ref({ ...vacio })
const form = ref({ ...vacio })
const mensaje = ref('')
const error = ref('')

const campos: { clave: keyof typeof vacio; label: string; placeholder: string; tipo?: string }[] = [
  { clave: 'nombre', label: 'Nombre', placeholder: 'Ingresá tu nombre' },
  { clave: 'apellido', label: 'Apellido', placeholder: 'Ingresá tu apellido' },
  { clave: 'mail', label: 'Correo electrónico', placeholder: 'nombre@ejemplo.com', tipo: 'email' },
  { clave: 'telefono', label: 'Teléfono', placeholder: 'Agregá tu teléfono', tipo: 'tel' },
  { clave: 'dni', label: 'DNI', placeholder: 'Ingresá tu documento' },
  { clave: 'fecha_nacimiento', label: 'Fecha de nacimiento', placeholder: 'DD / MM / AAAA', tipo: 'date' },
]

function mostrarDatos(datos: typeof vacio) {
  guardado.value = { ...vacio }
  for (const c of campos) guardado.value[c.clave] = datos[c.clave] ?? ''
  form.value = { ...guardado.value }
}

async function cargarPerfil() {
  const res = await fetch(`${API}/auth/medicos/perfil`, { headers }).catch(() => null)
  if (res?.ok) mostrarDatos(await res.json())
  else error.value = 'No se pudieron cargar tus datos.'
}

function cancelarCambios() {
  form.value = { ...guardado.value }
  mensaje.value = ''
  error.value = ''
}

async function guardarCambios() {
  mensaje.value = ''
  error.value = ''
  const res = await fetch(`${API}/auth/medicos/perfil`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({ ...form.value, fecha_nacimiento: form.value.fecha_nacimiento || null }),
  }).catch(() => null)
  const datos = await res?.json().catch(() => null)
  if (!res?.ok) {
    error.value = typeof datos?.detail === 'string' ? datos.detail : 'Revisá los datos ingresados.'
    return
  }
  mostrarDatos(datos)
  nombreUsuario.value = datos.nombre
  actualizarSesion({ nombre: datos.nombre })
  mensaje.value = 'Tus datos se guardaron correctamente.'
}

const foto = ref<string | null>(sesion.foto ?? null)

async function cambiarFoto(evento: Event) {
  mensaje.value = ''
  error.value = ''
  try {
    const nueva = await subirFoto(evento)
    if (!nueva) return
    foto.value = nueva
    mensaje.value = 'Tu foto se actualizó correctamente.'
  } catch (e) {
    error.value = (e as Error).message
  }
}

onMounted(cargarPerfil)

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))
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
      <button class="campoo" @click="emit('ir-a-chatbot')">
        MediBot<span class="campoo-indicador"></span>
      </button>
      <button class="campoo" @click="emit('ir-a-mis-pacientes')">
        Mis pacientes<span class="campoo-indicador"></span>
      </button>
      <button class="campoo" @click="emit('ir-a-solicitudes')">
        Solicitudes<span class="campoo-indicador"></span>
      </button>
      <button class="campoo" @click="emit('ir-a-MediPlus')">
        MediApp+<span class="campoo-indicador"></span>
      </button>
    </div>

    <div class="navbar-usuario-zona">
      <div class="navbar-divisor"></div>
      <button class="navbar-usuario" @click.stop="esta = !esta">
        <Avatar class="navbar-usuario-avatar" :foto="foto" :texto="nombreUsuario.charAt(0).toUpperCase()" />
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

        <button href="#" @click="emit('ir-a-mi-usuario')">
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

  <div class="min-h-screen lg:h-screen lg:overflow-hidden pt-[4.9rem] flex flex-col font-['Inter']">
    <div class="flex-1 min-h-0 px-4 sm:px-16 pt-6 pb-6 flex flex-col gap-5">
      <div class="shrink-0">
        <h1 class="text-3xl font-semibold text-[#182234]">Configuración</h1>
        <p class="text-sm text-[#61718B] mt-1">Administrá tu cuenta y la disponibilidad de tu consultorio.</p>
      </div>

      <div class="lg:flex-1 lg:min-h-0 flex flex-col lg:flex-row gap-6">
        <nav class="lg:w-60 shrink-0 p-5 bg-white rounded-2xl shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11)] flex flex-col gap-2 text-sm text-[#182234]">
          <div class="h-12 px-3 rounded-xl flex items-center gap-3 bg-[#EDF5FF] font-semibold text-[#3D6FC2]">
            <svg style="width: 1.25rem; height: 1.25rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></svg>
            Mi usuario
          </div>
          <button class="h-12 px-3 rounded-xl flex items-center gap-3 text-left cursor-pointer hover:bg-[#F4F7FB]" @click="emit('ir-a-seguridad')">
            <svg style="width: 1.25rem; height: 1.25rem" class="text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" /></svg>
            Seguridad
          </button>
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
            <h2 class="text-2xl font-semibold text-[#182234]">Mi usuario</h2>
            <p class="text-sm text-[#61718B] mt-1">Administrá tus datos personales y la información de tu cuenta.</p>
          </div>
          <div class="h-px shrink-0 bg-[#D7E2F0]"></div>

          <div class="lg:flex-1 lg:min-h-0 lg:overflow-y-auto flex flex-col gap-4">
            <div class="px-4 py-3 bg-[#EDF5FF] rounded-xl flex flex-wrap items-center gap-4">
              <Avatar class="size-14 shrink-0 rounded-full bg-white text-xl font-semibold text-[#3D6FC2] flex items-center justify-center" :foto="foto" :texto="nombreUsuario.charAt(0).toUpperCase()" />
              <div class="flex-1 min-w-0">
                <div class="text-lg font-semibold text-[#182234] truncate">{{ nombreUsuario }} · Cuenta profesional</div>
                <div class="text-xs text-[#61718B]">Tu foto ayuda a que los pacientes te reconozcan.</div>
              </div>
              <label class="w-full sm:w-56 h-12 px-4 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-white transition-colors flex items-center justify-center">
                Cambiar foto
                <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="cambiarFoto" />
              </label>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <label v-for="campo in campos" :key="campo.clave" class="flex flex-col gap-2">
                <span class="text-xs text-[#61718B]">{{ campo.label }}</span>
                <input v-model="form[campo.clave]" :type="campo.tipo || 'text'" :placeholder="campo.placeholder" class="h-12 px-4 bg-[#F4F7FB] rounded-xl outline-1 -outline-offset-1 outline-[#D7E2F0] text-sm text-[#182234] placeholder:text-[#182234] focus:outline-[#3D6FC2]" />
              </label>
            </div>

            <div class="px-4 py-3 bg-[#F4F7FB] rounded-xl flex flex-col gap-1">
              <span class="text-sm font-semibold text-[#182234]">Datos de tu cuenta</span>
              <span class="text-xs text-[#61718B]">Tus pacientes ven tu nombre, teléfono, correo y edad. El DNI y la fecha de nacimiento no se muestran.</span>
            </div>
          </div>

          <div class="shrink-0 mt-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span v-if="error" class="text-xs text-red-600">{{ error }}</span>
            <span v-else-if="mensaje" class="text-xs text-green-700">{{ mensaje }}</span>
            <span v-else class="text-xs text-[#61718B]">Los cambios se aplican al guardar.</span>
            <div class="flex gap-3">
              <button class="w-32 h-11 px-4 bg-[#F4F7FB] rounded-xl text-base font-medium text-[#3D6FC2] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="cancelarCambios">Cancelar</button>
              <button class="w-60 h-11 px-4 bg-[#3D6FC2] rounded-xl text-base font-medium text-white cursor-pointer hover:opacity-90 transition-opacity" @click="guardarCambios">Guardar cambios</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
