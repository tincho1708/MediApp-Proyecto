<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-principal-usuario', 'ir-a-chatbot', 'ir-a-calendario-usuario', 'ir-a-reservar-turno'])

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
        <button class="campoo" @click="emit('ir-a-reservar-turno')">Reservar Turno</button>
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
        <button class="campoo">Profesionales</button>
        <button class="campoo">Notificaciones</button>

        <button @click.stop="esta = !esta" class="barra">
          <div class="w-12 h-9 relative">
            <div class="w-12 border-t-2 border-black absolute left-0 top-0"></div>
            <div class="w-12 border-t-2 border-black absolute left-0 top-[1rem]"></div>
            <div class="w-12 border-t-2 border-black absolute left-0 top-[2rem]"></div>
          </div>
        </button>

        <div :class="['barra-desplegable', { 'barra-abierta': esta }]" @click.stop>
          <div href="#">
            <div id="barra-dentro" class="w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" style="flex-shrink: 0; width:1.375rem; height:1.375rem;">
                  <path d="M11.6219 32L10.9851 26.88C10.6401 26.7467 10.3154 26.5867 10.0107 26.4C9.70614 26.2133 9.40736 26.0133 9.11443 25.8L4.37811 27.8L0 20.2L4.0995 17.08C4.07297 16.8933 4.0597 16.7136 4.0597 16.5408V15.4608C4.0597 15.2869 4.07297 15.1067 4.0995 14.92L0 11.8L4.37811 4.2L9.11443 6.2C9.4063 5.98667 9.71144 5.78667 10.0299 5.6C10.3483 5.41333 10.6667 5.25333 10.9851 5.12L11.6219 0H20.3781L21.0149 5.12C21.3599 5.25333 21.6852 5.41333 21.9908 5.6C22.2965 5.78667 22.5948 5.98667 22.8856 6.2L27.6219 4.2L32 11.8L27.9005 14.92C27.927 15.1067 27.9403 15.2869 27.9403 15.4608V16.5392C27.9403 16.7131 27.9138 16.8933 27.8607 17.08L31.9602 20.2L27.5821 27.8L22.8856 25.8C22.5937 26.0133 22.2886 26.2133 21.9701 26.4C21.6517 26.5867 21.3333 26.7467 21.0149 26.88L20.3781 32H11.6219ZM14.408 28.8H17.5522L18.1095 24.56C18.932 24.3467 19.6951 24.0336 20.3988 23.6208C21.1025 23.208 21.7457 22.7077 22.3284 22.12L26.2687 23.76L27.8209 21.04L24.398 18.44C24.5307 18.0667 24.6236 17.6736 24.6766 17.2608C24.7297 16.848 24.7562 16.4277 24.7562 16C24.7562 15.5723 24.7297 15.1525 24.6766 14.7408C24.6236 14.3291 24.5307 13.9355 24.398 13.56L27.8209 10.96L26.2687 8.24L22.3284 9.92C21.7446 9.30667 21.1014 8.7936 20.3988 8.3808C19.6962 7.968 18.9331 7.6544 18.1095 7.44L17.592 3.2H14.4478L13.8905 7.44C13.068 7.65333 12.3054 7.96693 11.6028 8.3808C10.9002 8.79467 10.2565 9.2944 9.67164 9.88L5.73134 8.24L4.1791 10.96L7.60199 13.52C7.46932 13.92 7.37645 14.32 7.32338 14.72C7.27032 15.12 7.24378 15.5467 7.24378 16C7.24378 16.4267 7.27032 16.84 7.32338 17.24C7.37645 17.64 7.46932 18.04 7.60199 18.44L4.1791 21.04L5.73134 23.76L9.67164 22.08C10.2554 22.6933 10.8991 23.2069 11.6028 23.6208C12.3065 24.0347 13.0691 24.3477 13.8905 24.56L14.408 28.8ZM16.0796 21.6C17.6186 21.6 18.932 21.0533 20.0199 19.96C21.1078 18.8667 21.6517 17.5467 21.6517 16C21.6517 14.4533 21.1078 13.1333 20.0199 12.04C18.932 10.9467 17.6186 10.4 16.0796 10.4C14.5141 10.4 13.1938 10.9467 12.1186 12.04C11.0435 13.1333 10.5064 14.4533 10.5075 16C10.5085 17.5467 11.0461 18.8667 12.1202 19.96C13.1943 21.0533 14.5141 21.6 16.0796 21.6Z" fill="black"/>
                </svg>
                Configuracion
              </div>
            </div>
          </div>

          <button href="#" style="margin-top: auto;" @click="emit('ir-a-bienvenida')">
            <div class="barra-dentro-cerrar w-50 h-12 rounded-2xl">
              <div class="barra-texto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 31 32" fill="none" style="flex-shrink: 0; width:1.3125rem; height:1.375rem;">
                  <path d="M3.44444 32C2.49722 32 1.68663 31.6521 1.01267 30.9564C0.338704 30.2607 0.00114815 29.4234 0 28.4444V3.55556C0 2.57778 0.337556 1.74104 1.01267 1.04533C1.68778 0.34963 2.49837 0.00118519 3.44444 0H15.5V3.55556H3.44444V28.4444H15.5V32H3.44444ZM22.3889 24.8889L20.0208 22.3111L24.4125 17.7778H10.3333V14.2222H24.4125L20.0208 9.68889L22.3889 7.11111L31 16L22.3889 24.8889Z" fill="#FF2A2A"/>
                </svg>
                Cerrar sesion
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <div class="titulo-pagina w-fit text-zinc-900 text-4xl font-bold font-['Inter'] pb-2 mb-6 border-b-2 border-black">Configuracion</div>

    <div class="contenido-pagina flex gap-6 font-['Inter']">
      <div class="w-64 bg-white rounded-2xl border border-sky-500 shadow-[0px_4px_20px_2px_rgba(0,0,0,0.15)] p-4 flex flex-col gap-1 shrink-0">
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl bg-sky-500 text-white">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>
          Mi usuario
        </div>
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl text-black/70">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/></svg>
          Seguridad
        </div>
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl text-black/70">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.04-1.56V3a2 2 0 0 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 0 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15Z"/></svg>
          Preferencias
        </div>

        <div class="flex-1"></div>
        <hr class="border-zinc-200 my-2" />
        <button class="flex items-center gap-3 px-3 py-2 rounded-xl bg-red-100 text-red-500 font-medium" @click="emit('ir-a-bienvenida')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Cerrar sesion
        </button>
      </div>

      <div class="flex-1 bg-white rounded-2xl border border-sky-500 shadow-[0px_4px_20px_2px_rgba(0,0,0,0.15)] p-8">
        <div class="flex items-start gap-8">
          <div class="flex flex-col items-center shrink-0">
            <div class="w-28 h-28 rounded-full bg-zinc-100 border-2 border-sky-300 flex items-center justify-center">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#7dd3fc" stroke-width="1.5"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>
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
