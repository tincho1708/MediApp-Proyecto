<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-bienvenida'])

const opciones = ['Hoy', '1 Semana', '1 Mes', '1 Año']
const seleccionado = ref('Hoy')
const abierto = ref(false)

function seleccionar(opcion: string) {
  seleccionado.value = opcion
  abierto.value = false
}

function cerrarAlClickFuera() { abierto.value = false }

onMounted(() => document.addEventListener('click', cerrarAlClickFuera))
onBeforeUnmount(() => document.removeEventListener('click', cerrarAlClickFuera))
const esta = ref(true)
</script>

<template>
    <div class="navbar">

      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>

      <div class="navbar-acciones">
        <button class="campoo">MediBot</button>
        <button class="campoo">Mis pacientes</button>
        <button class="campoo">Notificaciones</button>
        <button class="campoo">MediApp+</button>
        <button @click="esta = !esta" class="barra">
          <div>──────</div>
          <div>──────</div>
          <div>──────</div>
        </button>

        <transition name="slide">
          <div v-if="esta" class="barra-desplegable">
            <a href="#">Inicio</a>
            <a href="#">Productos</a>
            <a href="#">Servicios</a>
            <a href="#">Contacto</a>
          </div>
        </transition>

      </div>

    </div>


    <div class ="bienvenida">Bienvenido, Matías</div>


    <div class ="content">

      <div class="resumen">
        <span class="resumen-label">Tu resumen de:</span>
        <div class="dropdown" @click.stop="abierto = !abierto">
          <button class="dropbtn">
            {{ seleccionado }}
            <svg class="flecha" :class="{ 'flecha-arriba': abierto }" xmlns="http://www.w3.org/2000/svg" width="15" height="9" viewBox="0 0 15 9" fill="none">
              <path d="M6.65666 8.07112C7.04719 8.46164 7.68035 8.46164 8.07088 8.07112L14.4348 1.70716C14.8254 1.31664 14.8254 0.68347 14.4348 0.292946C14.0443 -0.0975785 13.4111 -0.0975785 13.0206 0.292946L7.36377 5.9498L1.70692 0.292946C1.31639 -0.0975785 0.683226 -0.0975785 0.292702 0.292946C-0.0978227 0.68347 -0.0978227 1.31664 0.292702 1.70716L6.65666 8.07112ZM7.36377 5.36401H6.36377V7.36401H7.36377H8.36377V5.36401H7.36377Z" fill="white"/>
            </svg>
          </button>
          <transition name="fade-drop">
            <ul v-if="abierto" class="dropdown-menu">
              <li
                v-for="opcion in opciones"
                :key="opcion"
                class="dropdown-item"
                :class="{ activo: seleccionado === opcion }"
                @click.stop="seleccionar(opcion)"
              >
                {{ opcion }}
              </li>
            </ul>
          </transition>
        </div>
      </div>

    </div>

    <div class ="superior">
      <div class="cuadros">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="23" viewBox="0 0 20 23" fill="none">
            <path d="M10 12.65H15.5556V18.4H10V12.65ZM17.7778 2.3H16.6667V0H14.4444V2.3H5.55556V0H3.33333V2.3H2.22222C1 2.3 0 3.335 0 4.6V20.7C0 21.965 1 23 2.22222 23H17.7778C19 23 20 21.965 20 20.7V4.6C20 3.335 19 2.3 17.7778 2.3ZM17.7778 4.6V6.9H2.22222V4.6H17.7778ZM2.22222 20.7V9.2H17.7778V20.7H2.22222Z" fill="black"/>
          </svg>
          Agenda de hoy
      </div>
      <div class="cuadros"></div>
    </div>

    <div class="inferior">
      <div class="cuadro1">
        <div class="cuadro1-titulo">
          
        </div>
      </div>
    </div>

    <div class="div-derecho">
      <div class="calendario"></div>
    </div>

</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@100;200;300;400;500;600;700;800;900&display=swap');

.navbar {
  height: 100px;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #FFFFFF;
  box-sizing: border-box;
  padding: 8px 24px;
  z-index: 100;
}
.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-logo img {
  width: 110px;
  height: 110px;
}

.navbar-logo span {
  font-family: 'Lexend', sans-serif;
  font-size: 43px;
  font-weight: 700;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -14px;
  margin-top: 7px;
}

.navbar-acciones {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-direction: row;
  gap: 50px;
}
.campoo {
  width: 200px;
  height: 55px;
  background: #2E9CE0;
  border-radius: 40px;
  color: #000;
  text-align: center;
  font-family: Lexend;
  font-size: 24px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  border: none;
  cursor: pointer;
}

.barra {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-right: 20px;
  border-radius: 8px;
  border: 8px solid transparent;
}
.barra:hover {
  background-color: rgba(33, 133, 218, 0.5);
  transition: background-color 0.4s ease, transform 0.3s ease;
}

.barra-desplegable {
  position: fixed;
  top: 100px;
  right: 0;
  height: 300px;
  width: 220px;
  border-radius: 0 0 0 20px;
  display: flex;
  flex-direction: column;   
  gap: 8px;

  background: linear-gradient(160deg, #6366f1, #8b5cf6);
  padding: 24px 16px;
  box-shadow: -8px 0 24px rgba(99, 102, 241, 0.35);
}

.barra-desplegable a {
  color: #fff;
  text-decoration: none;
  font-family: system-ui, sans-serif;
  font-weight: 500;
  padding: 10px 16px;
  border-radius: 8px;
  transition: 0.25s;
}

.barra-desplegable a:hover {
  background: rgba(255, 255, 255, 0.2);
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.bienvenida {
  color: #000;
  font-family: Lexend;
  font-size: 58px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  margin-top: 130px;
  text-align: center;
}

.content {
  display: flex;
  flex-direction: column;
}

.resumen {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.resumen-label {
  color: #000;
  font-family: Lexend;
  font-size: 35px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  margin-left: 80px;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropbtn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #2E9CE0;
  color: #fff;
  font-family: 'Lexend', sans-serif;
  font-size: 15px;
  font-weight: 400;
  padding: 12px 24px;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(33, 133, 218, 0.35);
  transition: box-shadow 0.2s;
  user-select: none;
  margin-top: 5px;
}

.dropbtn:hover {
  box-shadow: 0 6px 18px rgba(33, 133, 218, 0.5);
}

.flecha {
  display: inline-block;
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.flecha-arriba {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  list-style: none;
  margin: 0;
  padding: 8px 0;
  min-width: 160px;
  z-index: 200;
  overflow: hidden;
}

.dropdown-item {
  font-family: 'Lexend', sans-serif;
  font-size: 16px;
  color: #333;
  padding: 12px 24px;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: #f0f7ff;
  color: #1F6BC6;
}

.dropdown-item.activo {
  color: #1F6BC6;
  font-weight: 600;
  background: #e8f3ff;
}

.fade-drop-enter-active,
.fade-drop-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-drop-enter-from,
.fade-drop-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.superior {
  display: flex;
  flex-direction: row;
  margin-top: 20px;
  margin-left: 65px;
  gap: 20px;
  width: 50%;
}

.inferior {
  width: 50%;
}

.cuadros {
  width: 258px;
  height: 177px;
  border-radius: 20px;
  border: 3px solid #2E9CE0;
  background: #FFF;
  box-shadow: 0 4px 10.7px 5px rgba(0, 0, 0, 0.25);
  margin-left: 18.5px;
  padding: 10px 15px;
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.cuadros svg {
  width: 20px;
  height: 23px;
  fill: black;
  margin-top: -4px;
}
.cuadro1 {
  border-radius: 20px;
  border: 5px solid #2E9CE0;
  background: #FFF;
  box-shadow: 0 4px 10.7px 5px rgba(0, 0, 0, 0.25);
  width: 552px;
  height: 267px;
  margin-left: 80px;
  margin-top: 20px;
  padding: 20px 20px;
}

.cuadro1-titulo {
  display: flex;
  gap: 10px;
  font-family: 'Lexend', sans-serif;
  font-size: 18px;
  font-weight: 500;
  color: #000;
}

.div-derecho {
  position: fixed;
  top: 287px;
  right: 80px;
}

.calendario {
  border-radius: 20px;
  border: 5px solid #2E9CE0;
  background: #FFF;
  box-shadow: 0 4px 10.7px 5px rgba(0, 0, 0, 0.25);
  width: 650px;
  height: 468px;
}
</style>
