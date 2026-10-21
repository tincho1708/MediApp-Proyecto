<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-chatbot', 'ir-a-principal', 'ir-a-solicitudes', 'ir-a-mis-pacientes', 'ir-a-configuracion'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const planes = [
  { nombre: 'MediApp Basic', descripcion: 'Para comenzar a organizar tu práctica.', precio: 'USD 0', periodo: 'por mes', destacado: false, beneficios: ['Caracteres limitados en la información de turnos', 'Caracteres limitados en tu perfil profesional'], boton: 'Elegir Basic' },
  { nombre: 'MediApp+', descripcion: 'Más alcance y espacio para tu práctica.', precio: 'USD 14,99', periodo: 'por mes', destacado: true, beneficios: ['Prioridad en el buscador de profesionales', 'Caracteres ilimitados en la información de turnos', 'Conexiones ilimitadas'], boton: 'Elegir MediApp+' },
  { nombre: 'MediApp Business', descripcion: 'Una opción para equipos de profesionales.', precio: 'USD 499', periodo: 'por año', destacado: false, beneficios: ['Hasta 50 usuarios', 'Caracteres ilimitados en la información de turnos', 'Conexiones ilimitadas'], boton: 'Elegir Business' },
]
</script>

<template>
  <div>
    <div class="navbar">
      <button @click="emit('ir-a-principal')">
        <div class="navbar-logo">
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

    <div class="min-h-screen lg:h-screen lg:overflow-hidden bg-linear-to-br from-blue-100 via-violet-100 to-blue-200 pt-[4.9rem] flex flex-col font-['Inter']">
      <div class="flex-1 min-h-0 max-w-328 w-full mx-auto px-4 sm:px-8 pt-8 pb-6 flex flex-col gap-6">
        <div class="shrink-0">
          <h1 class="text-3xl font-semibold text-gray-800">Nuestros planes, adaptados a cada cliente</h1>
          <p class="text-sm text-slate-500 mt-2">Compará las opciones y elegí la que mejor se adapte a tu trabajo.</p>
        </div>

        <div class="lg:flex-1 min-h-0 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="plan in planes" :key="plan.nombre" class="min-h-0 bg-white rounded-3xl p-6 flex flex-col gap-4" :class="plan.destacado ? 'outline-1 -outline-offset-1 outline-[#3D6FC2] shadow-[0_0_1.2rem_0.5rem_rgba(66,124,174,0.25)]' : 'outline-1 -outline-offset-1 outline-slate-200 shadow-[0_0.5rem_1.5rem_-0.25rem_rgba(34,66,105,0.11),0_0.125rem_0.375rem_0_rgba(34,66,105,0.06)]'">
            <div class="shrink-0 flex flex-col gap-2">
              <h2 class="text-2xl font-semibold text-gray-800">{{ plan.nombre }}</h2>
              <p class="text-sm text-slate-500">{{ plan.descripcion }}</p>
            </div>

            <div class="shrink-0 flex flex-col gap-1">
              <span class="text-5xl font-semibold text-gray-800">{{ plan.precio }}</span>
              <span class="text-sm text-slate-500">{{ plan.periodo }}</span>
            </div>

            <div class="shrink-0 h-px bg-slate-200"></div>

            <ul class="flex flex-col gap-4">
              <li v-for="beneficio in plan.beneficios" :key="beneficio" class="flex items-start gap-3 text-sm text-gray-800">
                <svg style="width: 1.25rem; height: 1.25rem" class="shrink-0 text-[#3D6FC2]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
                {{ beneficio }}
              </li>
            </ul>

            <button class="mt-auto shrink-0 h-11 rounded-xl text-sm font-medium cursor-pointer transition-opacity hover:opacity-90" :class="plan.destacado ? 'bg-[#3D6FC2] text-white' : 'bg-white outline-1 -outline-offset-1 outline-slate-200 text-[#3D6FC2]'">{{ plan.boton }}</button>
          </div>
        </div>

        <div class="shrink-0 p-4 bg-white rounded-2xl flex items-center gap-3 text-sm text-slate-500">
          <svg style="width: 1.25rem; height: 1.25rem" class="shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9" /><path d="M12 16v-4M12 8h.01" /></svg>
          Basic y MediApp+ se muestran por mes. Business se muestra por año.
        </div>
      </div>
    </div>
  </div>
</template>
