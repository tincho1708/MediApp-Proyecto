<script setup lang="ts">
const emit = defineEmits([
  'ir-a-bienvenida',
  'ir-a-chatbot',
  'ir-a-principal',
  'ir-a-solicitudes',
  'ir-a-mis-pacientes',
  'ir-a-configuracion',
])
import { ref, onMounted, onBeforeUnmount } from 'vue'

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
      <button class="campoo activo">MediApp+<span class="campoo-indicador"></span></button>
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
          <div class="dropdown-rol">Cuenta de médico</div>
        </div>
        <div class="dropdown-divisor"></div>


        <button @click="emit('ir-a-configuracion')">
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
  <div class="text-center text-black text-5xl font-normal font-['Inter']" style="margin-top: 9rem; padding: 0 2rem">
    Nuestros planes, adaptados a cada cliente.
  </div>
  <div style="display: flex; flex-direction: row; gap: 5rem; justify-content: center; margin-top: 2rem">
    <div class="w-80 h-[29.375rem] bg-white rounded-[1.25rem] mt-5 shadow-[0rem_0.25rem_0.66875rem_0.3125rem_rgba(0,0,0,0.25)] border-[0.3125rem] border-sky-500 p-6 text-left font-['Inter']">
      <div class="text-2xl font-semibold text-black">MediApp Basic</div>
      <div class="mt-3 flex items-end gap-1">
        <span class="text-4xl font-bold text-black">0$</span>
        <span class="text-xs text-black/60 leading-tight">USD/<br />mes</span>
      </div>
      <ul class="mt-6 space-y-3 text-black text-sm list-disc pl-5">
        <li>Caracteres limitados en informacion de turnos</li>
        <li>Caracteres limitados de infromacion como profesional</li>
      </ul>
    </div>

    <div class="w-80 h-[29.375rem] bg-white rounded-[1.25rem] mt-5 shadow-[0rem_0.25rem_0.66875rem_0.3125rem_rgba(0,0,0,0.25)] border-[0.3125rem] border-sky-500 p-6 text-left font-['Inter']">
      <div class="text-2xl font-semibold text-black">MediApp+ (plus)</div>
      <div class="mt-3 flex items-end gap-1">
        <span class="text-4xl font-bold text-black">14.99$</span>
        <span class="text-xs text-black/60 leading-tight">USD/<br />mes</span>
      </div>
      <ul class="mt-6 space-y-3 text-black text-sm list-disc pl-5">
        <li>Prioridad en el buscador de profesionales</li>
        <li>Caracteres ilimitados en la informacion de turnos</li>
        <li>Conexiones ilimitadas</li>
        <li>
          Cuento con conocimiento nulo relacionado a que beneficio insertar en este cuadro de texto.
        </li>
        <li>Algo que tenga sentido, no como lo de arriba</li>
      </ul>
    </div>

    <div class="w-80 h-[29.375rem] bg-white rounded-[1.25rem] mt-5 shadow-[0rem_0.25rem_0.66875rem_0.3125rem_rgba(0,0,0,0.25)] border-[0.3125rem] border-sky-500 p-6 text-left font-['Inter']">
      <div class="text-2xl font-semibold text-black">MediApp Business</div>
      <div class="mt-3 flex items-end gap-1">
        <span class="text-4xl font-bold text-black">499$</span>
        <span class="text-xs text-black/60 leading-tight">USD/<br />año</span>
      </div>
      <ul class="mt-6 space-y-3 text-black text-sm list-disc pl-5">
        <li>50 usuarios</li>
        <li>Caracteres ilimitados en la informacion de turnos</li>
        <li>Conexiones ilimitadas</li>
        <li>
          Cuento con conocimiento nulo relacionado a que beneficio insertar en este cuadro de texto.
        </li>
        <li>Algo que tenga sentido, no como lo de arriba</li>
      </ul>
    </div>
  </div>
</template>

<style></style>
