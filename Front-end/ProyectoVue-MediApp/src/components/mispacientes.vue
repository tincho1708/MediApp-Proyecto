<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useTurnosMedico } from '@/stores/turnosMedico'

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
])
const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() {
  esta.value = false
}

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const { turnos, cargando, error, usarPollingTurnos } = useTurnosMedico()

usarPollingTurnos()

const busqueda = ref('')

const pacientes = computed(() => {
  const ahora = Date.now()
  const porPaciente = new Map<
    number,
    { id: number; nombre: string; apellido: string; notas: string | null; fecha_hora: string }
  >()

  for (const t of turnos.value) {
    if (t.estado.estado !== 'aceptado') continue
    if (new Date(t.fecha_hora).getTime() < ahora) continue

    const actual = porPaciente.get(t.paciente.id)
    if (!actual || new Date(t.fecha_hora) < new Date(actual.fecha_hora)) {
      porPaciente.set(t.paciente.id, {
        id: t.paciente.id,
        nombre: t.paciente.nombre,
        apellido: t.paciente.apellido,
        notas: t.notas,
        fecha_hora: t.fecha_hora,
      })
    }
  }

  const lista = [...porPaciente.values()]
  const filtro = busqueda.value.trim().toLowerCase()
  const filtrada = filtro
    ? lista.filter((p) => `${p.nombre} ${p.apellido}`.toLowerCase().includes(filtro))
    : lista

  return filtrada.sort(
    (a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime(),
  )
})

const coloresAvatar = ['#E0645C', '#6CC26A', '#E0A75C', '#5C9EE0', '#9C6CE0', '#5CC2B0']
function colorAvatar(id: number) {
  return coloresAvatar[id % coloresAvatar.length]
}
function iniciales(p: { nombre: string; apellido: string }) {
  return `${p.nombre.charAt(0)}${p.apellido.charAt(0)}`.toUpperCase()
}
function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()}/${f.getMonth() + 1}/${f.getFullYear()}`
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
      <button class="campoo activo">Mis pacientes<span class="campoo-indicador"></span></button>
      <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes<span class="campoo-indicador"></span></button>
      <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+<span class="campoo-indicador"></span></button>
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

  <div class="titulo-pagina w-fit text-zinc-900 text-4xl font-semibold font-['Inter'] pb-2 mb-6 border-b-2 border-black">
    Mis pacientes
  </div>

  <div class="contenido-pagina">
    <div class="relative w-full max-w-[40rem] mb-8">
      <span class="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400">
        <svg style="width: 1.25rem; height: 1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
          <circle cx="11" cy="11" r="7" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </span>
      <input v-model="busqueda" type="text" placeholder="Buscar por nombre..." class="w-full pl-11 pr-4 py-3 border-b-2 border-black bg-transparent focus:outline-none text-lg font-['Inter']" />
    </div>

    <p v-if="cargando" class="text-black">Cargando pacientes...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <p v-else-if="!pacientes.length" class="text-black text-xl">
      No tenés pacientes con turnos próximos.
    </p>

    <div v-else class="flex flex-wrap gap-6">
      <div v-for="p in pacientes" :key="p.id" class="w-[26rem] bg-white rounded-[1.5rem] shadow-[0rem_0.25rem_1.25rem_0.125rem_rgba(0,0,0,0.25)] p-5 flex flex-col gap-4 font-['Inter']">
        <div class="flex flex-row gap-4">
          <div class="flex flex-col items-center gap-2 shrink-0">
            <div class="size-[7rem] rounded-full flex items-center justify-center text-white text-3xl font-medium" :style="{ backgroundColor: colorAvatar(p.id) }">
              {{ iniciales(p) }}
            </div>
            <span class="px-4 py-1 rounded-full border border-black text-sm whitespace-nowrap">{{
              formatearFecha(p.fecha_hora)
            }}</span>
          </div>

          <div class="flex-1 flex flex-col">
            <div class="text-2xl font-medium">{{ p.nombre }} {{ p.apellido }}</div>
            <div class="text-center text-black/60 mt-2 mb-1">Notas rapidas</div>
            <div class="flex-1 border border-black rounded-xl p-3 text-sm text-black/80">
              {{ p.notas || 'Sin notas.' }}
            </div>
          </div>
        </div>

        <button class="w-full py-2.5 rounded-xl bg-sky-500 text-white font-medium hover:bg-sky-600">
          Mas informacion
        </button>
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
