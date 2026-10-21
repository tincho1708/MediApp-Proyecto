<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-calendario-usuario', 'ir-a-reservar-turno', 'ir-a-notificaciones'])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const form = ref({
  nombre: '',
  apellido: '',
  email: '',
  telefono: '',
  direccion: '',
  ciudad: '',
  codigoPostal: '',
})

function cancelarCambios() {
  form.value = { nombre: '', apellido: '', email: '', telefono: '', direccion: '', ciudad: '', codigoPostal: '' }
}

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))
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
        <button class="campoo" @click="emit('ir-a-notificaciones')">Notificaciones<span v-if="conteoNoLeidas > 0" class="campoo-punto"></span><span class="campoo-indicador"></span></button>
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

          <div class="dropdown-item dropdown-item-destacado">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            Configuración
          </div>

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

    <div class="titulo-pagina w-fit text-zinc-900 text-4xl font-bold font-['Inter'] pb-2 mb-6 border-b-2 border-black">Mi usuario</div>

    <div class="contenido-pagina flex gap-6 font-['Inter']">
      <div class="w-64 bg-white rounded-2xl border border-sky-500 shadow-[0rem_0.25rem_1.25rem_0.125rem_rgba(0,0,0,0.15)] p-4 flex flex-col gap-1 shrink-0">
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl bg-sky-500 text-white">
          <svg style="width:1.125rem; height:1.125rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>
          Mi usuario
        </div>
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl text-black/70">
          <svg style="width:1.125rem; height:1.125rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/></svg>
          Seguridad
        </div>
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl text-black/70">
          <svg style="width:1.125rem; height:1.125rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.04-1.56V3a2 2 0 0 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 0 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15Z"/></svg>
          Preferencias
        </div>

        <div class="flex-1"></div>
        <hr class="border-zinc-200 my-2" />
        <button class="flex items-center gap-3 px-3 py-2 rounded-xl bg-red-100 text-red-500 font-medium" @click="emit('ir-a-bienvenida')">
          <svg style="width:1.125rem; height:1.125rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Cerrar sesion
        </button>
      </div>

      <div class="flex-1 bg-white rounded-2xl border border-sky-500 shadow-[0rem_0.25rem_1.25rem_0.125rem_rgba(0,0,0,0.15)] p-8">
        <div class="flex items-start gap-8">
          <div class="flex flex-col items-center shrink-0">
            <div class="w-28 h-28 rounded-full bg-zinc-100 border-2 border-sky-300 flex items-center justify-center">
              <svg style="width:3rem; height:3rem;" viewBox="0 0 24 24" fill="none" stroke="#7dd3fc" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>
            </div>
            <button class="mt-3 px-5 py-2 rounded-full bg-sky-500 text-white text-sm font-semibold">Cambiar foto</button>
          </div>

          <div class="flex-1 grid grid-cols-2 gap-x-6 gap-y-4">
            <div class="col-span-2">
              <label class="block text-sm font-semibold text-black mb-1">Nombre</label>
              <input v-model="form.nombre" type="text" placeholder="Ingresa tu nombre" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-semibold text-black mb-1">Apellido</label>
              <input v-model="form.apellido" type="text" placeholder="Ingresa tu apellido" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-black mb-1">Correo electrónico</label>
              <input v-model="form.email" type="email" placeholder="nombre@ejemplo.com" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-black mb-1">Teléfono</label>
              <input v-model="form.telefono" type="tel" placeholder="+54 11 0000 0000" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-semibold text-black mb-1">Dirección</label>
              <input v-model="form.direccion" type="text" placeholder="Ingresa tu dirección" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-black mb-1">Ciudad</label>
              <input v-model="form.ciudad" type="text" placeholder="Ingresa tu ciudad" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-black mb-1">Código postal</label>
              <input v-model="form.codigoPostal" type="text" placeholder="Ingresa tu código postal" class="w-full rounded-xl bg-zinc-50 border border-zinc-200 px-4 py-2.5 text-zinc-700 placeholder-zinc-400" />
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-8">
          <button class="px-6 py-2.5 rounded-xl bg-zinc-100 text-zinc-700 font-medium hover:bg-zinc-200" @click="cancelarCambios">Cancelar</button>
          <button class="px-6 py-2.5 rounded-xl bg-sky-500 text-white font-semibold hover:bg-sky-600">Guardar cambios</button>
        </div>
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
