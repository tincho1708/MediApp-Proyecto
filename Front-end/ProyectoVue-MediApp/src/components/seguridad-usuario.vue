<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const emit = defineEmits([
  'ir-a-profesionales',
  'ir-a-bienvenida',
  'ir-a-principal-usuario',
  'ir-a-chatbot',
  'ir-a-reservar-turno',
  'ir-a-notificaciones',
  'ir-a-mi-usuario-paciente',
])
const { conteoNoLeidas, usarPollingConteoNoLeidas } = useConteoNoLeidas()
usarPollingConteoNoLeidas()

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))
</script>

<template>
  <div>
    <div class="navbar">
      <button @click="emit('ir-a-principal-usuario')">
        <div class="navbar-logo" style="cursor: pointer">
          <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
          <span>App</span>
        </div>
      </button>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-reservar-turno')">
          Reservar turno<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-chatbot')">
          MediBot<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-profesionales')">
          Profesionales<span class="campoo-indicador"></span>
        </button>
        <button class="campoo" @click="emit('ir-a-notificaciones')">
          Notificaciones<span v-if="conteoNoLeidas > 0" class="campoo-punto"></span><span class="campoo-indicador"></span>
        </button>
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
            <div class="dropdown-rol">Cuenta de paciente</div>
          </div>
          <div class="dropdown-divisor"></div>

          <div class="dropdown-item dropdown-item-destacado" @click="emit('ir-a-mi-usuario-paciente')">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            Configuración
          </div>

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

    <div class="titulo-pagina font-['Inter'] mb-6">
      <div class="text-3xl font-semibold text-zinc-900">Configuración</div>
      <div class="text-sm text-[#61718B] mt-2">Administrá la contraseña de acceso a tu cuenta.</div>
    </div>

    <div class="contenido-pagina flex gap-6 font-['Inter'] text-sm font-medium">
      <div class="w-60 bg-white rounded-3xl border border-[#D7E2F0] shadow-[0px_8px_24px_-4px_rgba(34,66,105,0.11)] p-5 flex flex-col gap-2 shrink-0 text-[#61718B]">
        <button class="flex items-center gap-3 p-3 rounded-xl hover:bg-[#F8FAFC]" @click="emit('ir-a-mi-usuario-paciente')">
          <svg style="width: 1.125rem; height: 1.125rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          Mi usuario
        </button>
        <div class="flex items-center gap-3 p-3 rounded-xl bg-[#EDF5FF] text-[#176FB7]">
          <svg style="width: 1.125rem; height: 1.125rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
          </svg>
          Seguridad
        </div>
        <div class="flex items-center gap-3 p-3 rounded-xl">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2.5V4.16667M10 15.8333V17.5M2.5 10H4.16667M15.8333 10H17.5M4.66667 4.66667L5.83333 5.83333M14.1667 14.1667L15.3333 15.3333M4.66667 15.3333L5.83333 14.1667M14.1667 5.83333L15.3333 4.66667M13.3333 10C13.3333 10.8841 12.9821 11.7319 12.357 12.357C11.7319 12.9821 10.8841 13.3333 10 13.3333C9.11594 13.3333 8.2681 12.9821 7.64298 12.357C7.01786 11.7319 6.66667 10.8841 6.66667 10C6.66667 9.11594 7.01786 8.2681 7.64298 7.64298C8.2681 7.01786 9.11594 6.66667 10 6.66667C10.8841 6.66667 11.7319 7.01786 12.357 7.64298C12.9821 8.2681 13.3333 9.11594 13.3333 10Z" stroke-width="1.41667" stroke-linecap="round" stroke-linejoin="round" stroke="#61718B"/>
          </svg>
          Preferencias
        </div>

        <button class="mt-auto flex items-center gap-3 p-3 rounded-xl text-[#BE185D]" @click="emit('ir-a-bienvenida')">
          <svg style="width: 1.125rem; height: 1.125rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Cerrar sesión
        </button>
      </div>

      <div class="flex-1 min-h-142 bg-white rounded-3xl border border-[#D7E2F0] shadow-[0px_8px_24px_-4px_rgba(34,66,105,0.11)] p-6 flex flex-col">
        <div class="mb-4">
          <div class="text-lg font-semibold text-zinc-900">Seguridad</div>
          <div class="text-sm font-normal text-[#61718B]">Elegí una nueva contraseña para tu cuenta.</div>
        </div>

        <div class="w-full bg-[#F4F7FB] rounded-2xl p-6 flex flex-col gap-4">
          <div class="flex items-center gap-3 text-lg font-semibold text-zinc-900">
            <svg class="w-5 h-5 text-[#176FB7]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="5" y="11" width="14" height="10" rx="2" />
              <path d="M8 11V7a4 4 0 0 1 8 0v4" />
            </svg>
            Cambiar contraseña
          </div>

          <div v-for="campo in [
            { label: 'Contraseña actual', placeholder: '••••••••••••' },
            { label: 'Nueva contraseña', placeholder: 'Ingresá tu nueva contraseña' },
            { label: 'Confirmar nueva contraseña', placeholder: 'Repetí tu nueva contraseña' },]" :key="campo.label">
            <label class="block text-sm font-medium text-zinc-900 mb-1.5">{{ campo.label }}</label>
            <input type="password" :placeholder="campo.placeholder" class="w-full h-11 rounded-xl bg-white border border-[#D7E2F0] px-4 text-sm font-normal text-zinc-900 placeholder-zinc-900 focus:outline-none focus:border-[#176FB7]" />
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-auto pt-6">
          <button class="w-32 h-11 rounded-xl border border-[#D7E2F0] bg-white text-[#176FB7] text-sm font-medium hover:bg-[#EDF5FF]">
            Cancelar
          </button>
          <button class="w-52 h-11 rounded-xl bg-[#4270B0] text-white text-sm font-medium hover:bg-[#365E96]">
            Actualizar contraseña
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.titulo-pagina {
  margin-top: 6rem;
  margin-left: 2.5rem;
}

.contenido-pagina {
  margin-left: 2.5rem;
  margin-right: 2.5rem;
}
</style>
