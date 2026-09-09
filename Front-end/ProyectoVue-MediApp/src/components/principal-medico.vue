<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida', 'ir-a-chatbot', 'ir-a-calendario', 'ir-a-MediPlus', 'ir-a-solicitudes'])

const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
const nombreUsuario = sesion.nombre || 'Usuario'

const esta = ref(false)

function cerrarAlClickFuera() { esta.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))

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
        <button class="campoo" @click="emit('ir-a-chatbot')">MediBot</button>
        <button class="campoo">Mis pacientes</button>
        <button class="campoo" @click="emit('ir-a-solicitudes')">Solicitudes</button>
        <button class="campoo" @click="emit('ir-a-MediPlus')">MediApp+</button>

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

    <div class="bienvenida">Bienvenido, {{ nombreUsuario }}</div>

    <div class="main-layout">
      <div class="main-izquierdo">
        <div class="superior">
          <div class="cuadros">
            <div class="cuadros-titulo">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="23" viewBox="0 0 20 23" fill="none">
                <path d="M10 12.65H15.5556V18.4H10V12.65ZM17.7778 2.3H16.6667V0H14.4444V2.3H5.55556V0H3.33333V2.3H2.22222C1 2.3 0 3.335 0 4.6V20.7C0 21.965 1 23 2.22222 23H17.7778C19 23 20 21.965 20 20.7V4.6C20 3.335 19 2.3 17.7778 2.3ZM17.7778 4.6V6.9H2.22222V4.6H17.7778ZM2.22222 20.7V9.2H17.7778V20.7H2.22222Z" fill="black"/>
              </svg>
              Agenda de hoy
            </div>
            <div class="texto-agenda-hoy">
              3/5
              <div class="text-[0.9375rem]">Turnos Restantes</div>
            </div>
          </div>

          <div class="cuadros">
            <div class="cuadros-titulo">
              <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 31 31" fill="none">
                <path d="M15.4167 27.75C18.6877 27.75 21.8247 26.4506 24.1376 24.1376C26.4506 21.8247 27.75 18.6877 27.75 15.4167C27.75 12.1457 26.4506 9.00863 24.1376 6.69568C21.8247 4.38273 18.6877 3.08333 15.4167 3.08333C12.1457 3.08333 9.00863 4.38273 6.69568 6.69568C4.38273 9.00863 3.08333 12.1457 3.08333 15.4167C3.08333 18.6877 4.38273 21.8247 6.69568 24.1376C9.00863 26.4506 12.1457 27.75 15.4167 27.75ZM15.4167 0C17.4412 0 19.4459 0.398764 21.3164 1.17352C23.1868 1.94828 24.8863 3.08387 26.3179 4.51544C27.7495 5.94701 28.885 7.64653 29.6598 9.51696C30.4346 11.3874 30.8333 13.3921 30.8333 15.4167C30.8333 19.5054 29.2091 23.4267 26.3179 26.3179C23.4267 29.2091 19.5054 30.8333 15.4167 30.8333C6.89125 30.8333 0 23.8958 0 15.4167C0 11.3279 1.62425 7.40662 4.51544 4.51544C7.40662 1.62425 11.3279 0 15.4167 0ZM16.1875 7.70833V15.8021L23.125 19.9183L21.9688 21.8146L13.875 16.9583V7.70833H16.1875Z" fill="black"/>
              </svg>
              Próximo turno
            </div>
            <div class="proximo-turno-hora">09:30</div>
          </div>
        </div>

        <div class="inferior">
          <div class="cuadro1">
            <div class="cuadro1-titulo">Agenda de hoy</div>

            <div class="turno-fila" style="margin-top: 0.1rem;">
              09:30
              <div class="w-1.5 h-10 bg-indigo-400 rounded-[1.25rem]"></div>
              <div class="turno-info">
                <div class="turno-nombre">Juan liguori knoll</div>
                <div class="turno-detalle">Orientacion vocacional</div>
              </div>
            </div>

            <hr class="separador" />

            <div class="turno-fila">
              09:30
              <div class="w-1.5 h-10 bg-red-400 rounded-[1.25rem]"></div>
              <div class="turno-info">
                <div class="turno-nombre">Juan liguori knoll</div>
                <div class="turno-detalle">Orientacion vocacional</div>
              </div>
            </div>

            <hr class="separador" />

            <div class="turno-fila">
              09:30
              <div class="w-1.5 h-10 bg-green-400 rounded-[1.25rem]"></div>
              <div class="turno-info">
                <div class="turno-nombre">Juan liguori knoll</div>
                <div class="turno-detalle">Orientacion vocacional</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="div-derecho">
        <div class="calendario">
          <div class="cal-header">
            <button class="cal-nav-btn" @click="mesAnterior">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none">
                <path d="M29.2929 41.2929C28.9024 41.6834 28.9024 42.3166 29.2929 42.7071L35.6569 49.0711C36.0474 49.4616 36.6805 49.4616 37.0711 49.0711C37.4616 48.6805 37.4616 48.0474 37.0711 47.6569L31.4142 42L37.0711 36.3431C37.4616 35.9526 37.4616 35.3195 37.0711 34.9289C36.6805 34.5384 36.0474 34.5384 35.6569 34.9289L29.2929 41.2929ZM55 42V41H30V42V43H55V42Z" fill="black"/>
              </svg>
            </button>
            <span class="cal-titulo">{{ nombresMes[mesActual] }} {{ añoActual }}</span>
            <button class="cal-nav-btn" @click="mesSiguiente">
              <svg width="50" height="50" viewBox="0 0 83 82" fill="none" style="transform:rotate(180deg)">
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
  height: 5.4rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #FFFFFF;
  box-sizing: border-box;
  padding: 0.5rem 1.5rem;
  z-index: 100;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-logo img {
  width: 6.875rem;
  height: 6.875rem;
}

.navbar-logo span {
  font-family: Inter;
  font-size: 2.625rem;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -0.875rem;
  margin-top: 0.4375rem;
}

.navbar-acciones {
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 2.5rem;
}

.campoo {
  width: 12.875rem;
  height: 4.375rem;
  border-radius: 1.25rem;
  color: #000;
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 1.6rem;
  font-weight: 300;
  line-height: normal;
  cursor: pointer;
}

.campoo:hover {
  background-color: #C6E9FF;
  transition: background-color 0.2s ease;
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
  border: 0.0625rem #2E9CE0 solid;
  cursor: pointer;
  box-shadow: 0 0 0.70625rem 0.0625rem rgba(35, 106, 205, 0.67);
}

.boton-plus:hover {
  background-color: #2E9CE0;
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
  top: 6.25rem;
  right: 0;
  height: 21.875rem;
  width: 13.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.5rem 1rem;
  box-shadow: -0.5rem 0 1.5rem rgba(99, 102, 241, 0.35);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  pointer-events: none;
  border-radius: 1.3125rem;
  background: #E8E8E8;
  margin-top: 1%;
}

.barra-abierta {
  transform: translateX(0);
  pointer-events: auto;
}

#barra-dentro {
  align-items: center;
  display: flex;
  justify-content: center;
}

#barra-dentro:hover {
  background-color: #2E9CE0;
  transition: background-color 0.2s ease;
}

.barra-dentro-cerrar {
  align-items: center;
  display: flex;
  justify-content: center;
}

.barra-dentro-cerrar:hover {
  background-color: #fca5a5;
  transition: background-color 0.2s ease;
}

.barra-texto {
  width: 11rem;
  height: 2rem;
  color: #000;
  font-size: 1.375rem;
  font-weight: 400;
  font-family: 'Inter', sans-serif;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.bienvenida {
  color: #000;
  font-family: 'Inter', sans-serif;
  font-size: 3.625rem;
  font-weight: 400;
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
  border: 0.1875rem solid #2E9CE0;
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
  border: 0.3125rem solid #2E9CE0;
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

.separador {
  border: none;
  border-top: 0.0625rem solid rgba(0, 0, 0, 0.6);
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
  border: 0.3125rem solid #2E9CE0;
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
  font-weight: 500;
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
  color: #2E9CE0;
  font-weight: 700;
}

.cal-ver-completo {
  display: block;
  width: calc(100% - 2.5rem);
  margin: auto 1.25rem 1rem;
  padding: 0.875rem;
  background: #2E9CE0;
  color: #000;
  font-family: 'Inter', sans-serif;
  font-size: 1.325rem;
  font-weight: 500;
  border: none;
  border-radius: 1rem;
  cursor: pointer;
}
</style>
