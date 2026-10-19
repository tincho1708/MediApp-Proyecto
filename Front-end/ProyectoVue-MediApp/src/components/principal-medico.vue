<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTurnosMedico } from '@/stores/turnosMedico'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-solicitudes', 'ir-a-mis-pacientes', 'ir-a-configuracion', 'ir-a-mi-usuario'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

const { turnos, usarPollingTurnos } = useTurnosMedico()

usarPollingTurnos()

function esMismoDia(fechaHora: string, dia: Date) {
  const f = new Date(fechaHora)
  return f.getFullYear() === dia.getFullYear() && f.getMonth() === dia.getMonth() && f.getDate() === dia.getDate()
}

const turnosAceptados = computed(() => turnos.value.filter(t => t.estado?.estado === 'aceptado'))

const proximoTurno = computed(() => {
  const ahora = Date.now()
  return turnosAceptados.value
    .filter(t => new Date(t.fecha_hora).getTime() >= ahora)
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())[0] ?? null
})

const turnosHoy = computed(() => {
  const ahora = new Date()
  return turnosAceptados.value
    .filter(t => esMismoDia(t.fecha_hora, ahora))
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
})

const turnosHoyCompletados = computed(() => {
  const ahora = Date.now()
  return turnosHoy.value.filter(t => new Date(t.fecha_hora).getTime() < ahora).length
})

const proximosTurnos = computed(() => {
  const ahora = Date.now()
  return turnosAceptados.value
    .filter(t => new Date(t.fecha_hora).getTime() >= ahora)
    .sort((a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime())
    .slice(0, 3)
})

function formatearHora(fechaHora: string) {
  const f = new Date(fechaHora)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(f.getHours())}:${pad(f.getMinutes())}`
}
function formatearFecha(fechaHora: string) {
  const f = new Date(fechaHora)
  return `${f.getDate()}/${f.getMonth() + 1}`
}

const coloresAvatar = ['#E0645C', '#6CC26A', '#E0A75C', '#5C9EE0', '#9C6CE0', '#5CC2B0']
function colorPaciente(id: number) {
  return coloresAvatar[id % coloresAvatar.length]
}

const hoy = new Date()
const mesActual = ref(hoy.getMonth())
const añoActual = ref(hoy.getFullYear())

const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

function mesAnterior() {
  if (mesActual.value === 0) {
    mesActual.value = 11
    añoActual.value--
  } else {
    mesActual.value--
  }
}

function mesSiguiente() {
  if (mesActual.value === 11) {
    mesActual.value = 0
    añoActual.value++
  } else {
    mesActual.value++
  }
}

const celdas = computed(() => {
  const ultimoDia = new Date(añoActual.value, mesActual.value + 1, 0).getDate()
  const primerDia = new Date(añoActual.value, mesActual.value, 1).getDay()
  const offset = (primerDia + 6) % 7
  const resultado = []

  for (let i = 0; i < offset; i++) {
    resultado.push({ otroMes: true })
  }

  for (let d = 1; d <= ultimoDia; d++) {
    resultado.push({
      dia: d,
      hoy: d === hoy.getDate() && mesActual.value === hoy.getMonth() && añoActual.value === hoy.getFullYear(),
    })
  }

  let siguiente = 1
  while (resultado.length % 7 !== 0) {
    resultado.push({ dia: siguiente, otroMes: true })
    siguiente++
  }

  return resultado
})
</script>

<template>
  <div>
    <div class="navbar">
      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>

      <div class="navbar-acciones">
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot<span class="campoo-indicador"></span></button>
        <button class="campoo" @click="emit('ir-a-mis-pacientes')">Mis pacientes<span class="campoo-indicador"></span></button>
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
          <svg style="width:1rem; height:1rem;" class="navbar-usuario-chevron" :class="{ 'navbar-usuario-chevron-abierta': esta }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
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
                <circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>
              </svg>
              Mi cuenta
            </div>
          </button>

          <button href="#" @click="emit('ir-a-configuracion')">
            <div class="dropdown-item dropdown-item-destacado">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              Configuración
            </div>
          </button>

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

    <div class="bienvenida">Bienvenido, {{ nombreUsuario }}</div>

    <div class="main-layout">
      <div class="main-izquierdo">
        <div class="superior">
          <div class="cuadros">
            <div class="cuadros-titulo">
              <svg style="width:1.25rem; height:1.4375rem;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 23" fill="none">
                <path d="M10 12.65H15.5556V18.4H10V12.65ZM17.7778 2.3H16.6667V0H14.4444V2.3H5.55556V0H3.33333V2.3H2.22222C1 2.3 0 3.335 0 4.6V20.7C0 21.965 1 23 2.22222 23H17.7778C19 23 20 21.965 20 20.7V4.6C20 3.335 19 2.3 17.7778 2.3ZM17.7778 4.6V6.9H2.22222V4.6H17.7778ZM2.22222 20.7V9.2H17.7778V20.7H2.22222Z" fill="black"/>
              </svg>
              Agenda de hoy
            </div>
            <div class="texto-agenda-hoy">
              <template v-if="turnosHoy.length">
                {{ turnosHoyCompletados }}/{{ turnosHoy.length }}
                <div class="text-[0.9375rem]">Turnos de hoy</div>
              </template>
              <div v-else class="text-[1.25rem] text-center">No tenés turnos hoy</div>
            </div>
          </div>

          <div class="cuadros">
            <div class="cuadros-titulo">
              <svg style="width:1.875rem; height:1.875rem;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 31 31" fill="none">
                <path d="M15.4167 27.75C18.6877 27.75 21.8247 26.4506 24.1376 24.1376C26.4506 21.8247 27.75 18.6877 27.75 15.4167C27.75 12.1457 26.4506 9.00863 24.1376 6.69568C21.8247 4.38273 18.6877 3.08333 15.4167 3.08333C12.1457 3.08333 9.00863 4.38273 6.69568 6.69568C4.38273 9.00863 3.08333 12.1457 3.08333 15.4167C3.08333 18.6877 4.38273 21.8247 6.69568 24.1376C9.00863 26.4506 12.1457 27.75 15.4167 27.75ZM15.4167 0C17.4412 0 19.4459 0.398764 21.3164 1.17352C23.1868 1.94828 24.8863 3.08387 26.3179 4.51544C27.7495 5.94701 28.885 7.64653 29.6598 9.51696C30.4346 11.3874 30.8333 13.3921 30.8333 15.4167C30.8333 19.5054 29.2091 23.4267 26.3179 26.3179C23.4267 29.2091 19.5054 30.8333 15.4167 30.8333C6.89125 30.8333 0 23.8958 0 15.4167C0 11.3279 1.62425 7.40662 4.51544 4.51544C7.40662 1.62425 11.3279 0 15.4167 0ZM16.1875 7.70833V15.8021L23.125 19.9183L21.9688 21.8146L13.875 16.9583V7.70833H16.1875Z" fill="black"/>
              </svg>
              Próximo turno
            </div>
            <div v-if="proximoTurno" class="proximo-turno-hora">{{ formatearHora(proximoTurno.fecha_hora) }}</div>
            <div v-else class="text-[1.5rem] text-center mt-4">Sin turnos próximos</div>
          </div>
        </div>

        <div class="inferior">
          <div class="cuadro1">
            <div class="cuadro1-titulo">Proximos turnos</div>

            <p v-if="!proximosTurnos.length" class="text-black mt-4">No tenés turnos próximos.</p>

            <template v-for="(t, i) in proximosTurnos" :key="t.id_turno">
              <hr v-if="i > 0" class="separador-turno" />
              <div class="turno-fila" :style="i === 0 ? 'margin-top: 0.1rem;' : ''">
                <div class="flex flex-col items-center leading-tight w-14 shrink-0">
                  <span class="text-[0.85rem] text-black/70">{{ formatearFecha(t.fecha_hora) }}</span>
                  <span>{{ formatearHora(t.fecha_hora) }}</span>
                </div>
                <div class="w-1.5 h-10 rounded-[1.25rem]" :style="{ backgroundColor: colorPaciente(t.paciente.id) }"></div>
                <div class="turno-info">
                  <div class="turno-nombre">{{ t.paciente.nombre }} {{ t.paciente.apellido }}</div>
                  <div class="turno-detalle">{{ t.notas || 'Sin motivo especificado' }}</div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="div-derecho">
        <div class="calendario">
          <div class="cal-header">
            <button class="cal-nav-btn" @click="mesAnterior">
              <svg style="width:3.125rem; height:3.125rem;" viewBox="0 0 83 82" fill="none">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
            <span class="cal-titulo">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
            <button class="cal-nav-btn" @click="mesSiguiente">
              <svg viewBox="0 0 83 82" fill="none" style="transform:rotate(180deg); width:3.125rem; height:3.125rem;">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
          </div>

          <div class="cal-grid">
            <div class="cal-nombre-dia">LU</div>
            <div class="cal-nombre-dia">MA</div>
            <div class="cal-nombre-dia">MI</div>
            <div class="cal-nombre-dia">JU</div>
            <div class="cal-nombre-dia">VI</div>
            <div class="cal-nombre-dia">SA</div>
            <div class="cal-nombre-dia">DO</div>

            <div
              v-for="(celda, i) in celdas"
              :key="i"
              class="cal-dia"
              :class="{
                'cal-hoy': celda.hoy,
                'cal-otro-mes': celda.otroMes
              }"
            >
              {{ celda.dia }}
            </div>
          </div>

          <button class="cal-ver-completo" @click="emit('ir-a-calendario')">Ver calendario completo</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.navbar {
  height: 5rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  background-color: #FFFFFF;
  border-bottom: 0.0625rem solid #E2E8F0;
  box-shadow: 0 0.1875rem 0.625rem 0 rgba(24, 34, 52, 0.04);
  box-sizing: border-box;
  padding: 0 2rem 0 3rem;
  z-index: 100;
}

.navbar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-left: -1.4rem;
  cursor: pointer;
}

.navbar-logo img {
  width: 4.25rem;
  height: 4.25rem;
}

.navbar-logo span {
  font-family: Inter;
  font-size: 2.0625rem;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -0.5rem;
  margin-top: 0.25rem;
}

.navbar-acciones {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 1.7rem;
  margin-left: 14rem;
}

.campoo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  color: #1E293B;
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  font-weight: 500;
  line-height: normal;
  cursor: pointer;
}

.campoo:hover:not(.activo) {
  color: #0F172A;
}

.campoo-indicador {
  width: 3rem;
  height: 0.125rem;
  border-radius: 0.0625rem;
  background: transparent;
}

.campoo.activo {
  color: #0369A1;
}

.campoo.activo .campoo-indicador {
  background-color: #0369A1;
}

.navbar-usuario-zona {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  position: relative;
}

.navbar-divisor {
  width: 0.0625rem;
  height: 2.5rem;
  background-color: #E2E8F0;
}

.navbar-usuario {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #F8FAFC;
  border: none;
  border-radius: 1rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.navbar-usuario:hover {
  background-color: #F1F5F9;
}

.navbar-usuario-avatar {
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  border-radius: 1rem;
  background-color: #EFF6FF;
  color: #0369A1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
}

.navbar-usuario-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.navbar-usuario-nombre {
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.2;
}

.navbar-usuario-rol {
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  color: #64748B;
  line-height: 1.2;
}

.navbar-usuario svg {
  color: #64748B;
  flex-shrink: 0;
}

.navbar-usuario-chevron {
  transition: transform 0.2s ease;
}

.navbar-usuario-chevron-abierta {
  transform: rotate(180deg);
}

.boton-plus {
  width: 11.875rem;
  height: 4.375rem;
  background: #D8F0FF;
  border-radius: 1.25rem;
  color: #000;
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.5625rem;
  font-weight: 400;
  line-height: normal;
  border: 0.0625rem #3D6FC2 solid;
  cursor: pointer;
  box-shadow: 0 0 0.70625rem 0.0625rem rgba(35, 106, 205, 0.67);
}

.boton-plus:hover {
  background-color: #3D6FC2;
  transition: background-color 0.2s ease;
}

.barra {
  background: none;
  border: 0.5rem solid transparent;
  cursor: pointer;
  padding: 0.3125rem;
  margin-right: 1.25rem;
  border-radius: 0.5rem;
}

.barra:hover {
  background-color: rgba(33, 133, 218, 0.5);
  transition: background-color 0.4s ease, transform 0.3s ease;
}

.barra-desplegable {
  position: fixed;
  top: 6.75rem;
  right: 2rem;
  width: 18rem;
  height: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  box-shadow: 0 0.625rem 1.75rem -0.25rem rgba(24, 45, 75, 0.16),
              0 0.125rem 0.375rem 0 rgba(24, 45, 75, 0.06);
  outline: 0.0625rem solid #E2E8F0;
  outline-offset: -0.0625rem;
  transform: translateY(-1.5rem);
  opacity: 0;
  transition: transform 0.3s ease, opacity 0.3s ease;
  pointer-events: none;
  border-radius: 1rem;
  background: #FFFFFF;
}

.dropdown-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0 0.25rem;
}

.dropdown-nombre {
  font-family: 'Inter', sans-serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: #0F172A;
}

.dropdown-rol {
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  color: #64748B;
}

.dropdown-divisor {
  height: 0.0625rem;
  background-color: #E2E8F0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 1.0625rem;
  font-weight: 500;
  color: #0F172A;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.dropdown-item svg {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
  color: #0369A1;
}

.dropdown-item-destacado {
  background-color: #F8FAFC;
}

.dropdown-item-destacado:hover {
  background-color: #F1F5F9;
}

.dropdown-item-danger {
  color: #B91C1C;
}

.dropdown-item-danger svg {
  color: #B91C1C;
}

.dropdown-item-danger:hover {
  background-color: #FEF2F2;
}

.barra-abierta {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}

.barra-desplegable button {
  all: unset;
  box-sizing: border-box;
  width: 100%;
  cursor: pointer;
}

#barra-dentro {
  width: 100%;
  align-items: center;
  display: flex;
  justify-content: flex-start;
  padding-left: 0.4rem;
}

#barra-dentro:hover {
  background-color: #3D6FC2;
  transition: background-color 0.2s ease;
}

.barra-dentro-cerrar {
  width: 100%;
  align-items: center;
  display: flex;
  justify-content: flex-start;
  padding-left: 0.4rem;
}

.barra-dentro-cerrar:hover {
  background-color: #fca5a5;
  transition: background-color 0.2s ease;
}

.barra-texto {
  width: auto;
  height: 2rem;
  color: #000;
  font-size: 1.375rem;
  font-weight: 400;
  font-family: 'Inter', sans-serif;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.375rem;
}

.bienvenida {
  color: #000;
  font-family: 'Inter', sans-serif;
  font-size: 3.625rem;
  font-weight: 500;
  line-height: normal;
  margin-top: 7.5rem;
  text-align: center;
}

.main-layout {
  display: flex;
  align-items: stretch;
  gap: 4%;
  margin-top: 2.5rem;
}

.main-izquierdo {
  flex: 1;
}

.superior {
  display: flex;
  flex-direction: row;
  margin-top: 1.25rem;
  margin-left: 4.0625rem;
  gap: 1.25rem;
  width: 50%;
}

.cuadros {
  flex: 0 0 15.9375rem;
  width: 16.125rem;
  height: 11.0625rem;
  overflow: hidden;
  border-radius: 1.25rem;
  border: 0.1875rem solid #3D6FC2;
  background: #FFF;
  box-shadow: 0 0.25rem 0.66875rem 0.3125rem rgba(0, 0, 0, 0.25);
  margin-left: 1.15625rem;
  padding: 0.625rem 0.9375rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.cuadros-titulo {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.375rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
}

.cuadros svg {
  width: 1.5rem;
  height: 1.5rem;
  fill: black;
  margin-top: -0.25rem;
}

.texto-agenda-hoy {
  font-family: 'Inter', sans-serif;
  font-size: 3rem;
  font-weight: 500;
  color: #000;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 12.5rem;
  margin-left: 3%;
}

.proximo-turno-hora {
  font-family: 'Inter', sans-serif;
  font-size: 4.5rem;
  font-weight: 400;
  color: #000;
  text-align: center;
  margin-top: 1rem;
}

.inferior {
  width: 50%;
}

.cuadro1 {
  border-radius: 1.25rem;
  border: 0.3125rem solid #3D6FC2;
  background: #FFF;
  box-shadow: 0 0.25rem 0.66875rem 0.3125rem rgba(0, 0, 0, 0.25);
  width: 34.5rem;
  height: 16.6875rem;
  margin-left: 5rem;
  margin-top: 1.25rem;
  padding: 1.25rem;
}

.cuadro1-titulo {
  display: flex;
  gap: 0.625rem;
  font-family: 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #000;
}

.turno-fila {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-family: 'Inter', sans-serif;
  font-size: 1.5rem;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.75);
}

.turno-info {
  display: flex;
  flex-direction: column;
}

.turno-nombre {
  font-size: 1rem;
  font-weight: 400;
  color: #000;
}

.turno-detalle {
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.8);
}

.separador-turno {
  border: none;
  border-top: 0.125rem solid rgba(46, 156, 224, 0.5);
  margin: 0.375rem 0;
}

.div-derecho {
  flex-shrink: 0;
  margin-top: 1.25rem;
  margin-right: 5rem;
  display: flex;
}

.calendario {
  border-radius: 1.25rem;
  border: 0.3125rem solid #3D6FC2;
  background: #FFF;
  box-shadow: 0 0.25rem 0.66875rem 0.3125rem rgba(0, 0, 0, 0.25);
  width: 40.625rem;
  padding-bottom: 1rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.cal-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.25rem 0.625rem;
}

.cal-nav-btn {
  width: 3.5rem;
  height: 3.5rem;
  background: white;
  border: 0.0625rem solid black;
  border-radius: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.cal-titulo {
  flex: 1;
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.75rem;
  font-weight: 600;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 0 1rem;
  flex: 1;
  align-content: start;
}

.cal-nombre-dia {
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  padding: 0.625rem 0 0.375rem;
}

.cal-dia {
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  padding: 0.3125rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.cal-otro-mes {
  color: #aaa;
}

.cal-hoy {
  color: #3D6FC2;
  font-weight: 700;
}

.cal-ver-completo {
  display: block;
  width: calc(100% - 2.5rem);
  margin: auto 1.25rem 1rem;
  padding: 0.875rem;
  background: #3D6FC2;
  color: #000;
  font-family: 'Inter', sans-serif;
  font-size: 1.325rem;
  font-weight: 500;
  border: none;
  border-radius: 1rem;
  cursor: pointer;
}
</style>
