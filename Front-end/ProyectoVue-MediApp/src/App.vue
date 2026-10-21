<script setup lang="ts">
import { ref } from 'vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'
import MediBot from './components/MediBot.vue'
import Principal from './components/principal-medico.vue'
import Calendario from './components/calendario.vue'
import MediPlus from './components/MediPlus.vue'
import Solicitudes from './components/solicitudes.vue'
import MisPacientes from './components/mispacientes.vue'
import Disponibilidad from './components/disponibilidad.vue'
import MiUsuario from './components/MiUsuario.vue'
import PrincipalUsuario from './components/principal-usuario.vue'
import CalendarioUsuario from './components/calendario-usuario.vue'
import ReservarTurno from './components/reservar-turno.vue'
import Profesionales from './components/profesionales.vue'
import MiUsuarioPaciente from './components/MiUsuario-Paciente.vue'
import Notificaciones from './components/notificaciones.vue'
import { useTurnosMedico } from '@/stores/turnosMedico'
import { useConteoNoLeidas } from '@/stores/notificacionesConteo'

const { resetTurnosMedico } = useTurnosMedico()
const { resetConteoNoLeidas } = useConteoNoLeidas()

// Si ya hay una sesión guardada (por ej. al recargar la página), se entra directo a la pantalla principal
function vistaInicial() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  if (!sesion.token) return 'bienvenida'
  return sesion.tipo === 'Medico' ? 'Principal' : 'principalUsuario'
}

const vista = ref(vistaInicial())

// Fecha con la que abre el calendario del paciente (null = hoy)
const fechaCalendarioUsuario = ref<string | null>(null)
// Médico ya elegido al entrar a "Reservar turno" desde Profesionales (null = elegir en el paso 1)
const medicoReserva = ref<number | null>(null)

function irACalendarioUsuario(fecha?: string) {
  fechaCalendarioUsuario.value = fecha ?? null
  vista.value = 'calendarioUsuario'
}

function irAReservarTurno(medicoId?: number) {
  medicoReserva.value = medicoId ?? null
  vista.value = 'reservarTurno'
}

function cerrarSesion() {
  localStorage.removeItem('sesion')
  resetTurnosMedico()
  resetConteoNoLeidas()
  vista.value = 'bienvenida'
}
</script>

<template>
  <Transition name="fade">
    <!-- Acceso -->
    <Bienvenida v-if="vista === 'bienvenida'" key="bienvenida" @ir-a-registro="vista = 'registrar'" @ir-a-login="vista = 'iniciarSesion'" @ir-a-principal="vista = 'Principal'" @ir-a-principal-usuario="vista = 'principalUsuario'" />

    <Registrar v-else-if="vista === 'registrar'" key="registrar" @ir-a-login="vista = 'iniciarSesion'" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-principal-usuario="vista = 'principalUsuario'" />

    <IniciarSesion v-else-if="vista === 'iniciarSesion'" key="iniciarSesion" @bienvenida="vista = 'bienvenida'" @ir-a-registro="vista = 'registrar'" @ir-a-principal="vista = 'Principal'" @ir-a-principal-usuario="vista = 'principalUsuario'" />

    <!-- Compartida (médico y paciente) -->
    <MediBot v-else-if="vista === 'chatbot'" key="chatbot" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-calendario="vista = 'calendario'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-reservar-turno="irAReservarTurno()" @ir-a-profesionales="vista = 'profesionales'" @ir-a-calendario-usuario="irACalendarioUsuario()" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" @ir-a-notificaciones="vista = 'notificaciones'" />

    <!-- Médico -->
    <Principal v-else-if="vista === 'Principal'" key="principal" @ir-a-bienvenida="cerrarSesion" @ir-a-chatbot="vista = 'chatbot'" @ir-a-calendario="vista = 'calendario'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <Calendario v-else-if="vista === 'calendario'" key="calendario" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <MediPlus v-else-if="vista === 'MediPlus'" key="MediPlus" @ir-a-bienvenida="cerrarSesion" @ir-a-chatbot="vista = 'chatbot'" @ir-a-principal="vista = 'Principal'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <Solicitudes v-else-if="vista === 'solicitudes'" key="solicitudes" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-calendario="vista = 'calendario'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <MisPacientes v-else-if="vista === 'misPacientes'" key="misPacientes" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-calendario="vista = 'calendario'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-configuracion="vista = 'configuracion'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <Disponibilidad v-else-if="vista === 'configuracion'" key="configuracion" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-calendario="vista = 'calendario'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-mi-usuario="vista = 'miUsuario'" />

    <MiUsuario v-else-if="vista === 'miUsuario'" key="miUsuario" @ir-a-bienvenida="cerrarSesion" @ir-a-principal="vista = 'Principal'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-calendario="vista = 'calendario'" @ir-a-MediPlus="vista = 'MediPlus'" @ir-a-solicitudes="vista = 'solicitudes'" @ir-a-mis-pacientes="vista = 'misPacientes'" @ir-a-configuracion="vista = 'configuracion'" />

    <!-- Paciente -->
    <PrincipalUsuario v-else-if="vista === 'principalUsuario'" key="principalUsuario" @ir-a-bienvenida="cerrarSesion" @ir-a-chatbot="vista = 'chatbot'" @ir-a-reservar-turno="irAReservarTurno()" @ir-a-profesionales="vista = 'profesionales'" @ir-a-calendario-usuario="irACalendarioUsuario" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" @ir-a-notificaciones="vista = 'notificaciones'" />

    <CalendarioUsuario v-else-if="vista === 'calendarioUsuario'" key="calendarioUsuario" :fecha-inicial="fechaCalendarioUsuario" @ir-a-bienvenida="cerrarSesion" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-reservar-turno="irAReservarTurno()" @ir-a-profesionales="vista = 'profesionales'" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" @ir-a-notificaciones="vista = 'notificaciones'" />

    <ReservarTurno v-else-if="vista === 'reservarTurno'" key="reservarTurno" :medico-inicial-id="medicoReserva" @ir-a-bienvenida="cerrarSesion" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-profesionales="vista = 'profesionales'" @ir-a-calendario-usuario="irACalendarioUsuario" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" @ir-a-notificaciones="vista = 'notificaciones'" />

    <Profesionales v-else-if="vista === 'profesionales'" key="profesionales" @ir-a-bienvenida="cerrarSesion" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-reservar-turno="irAReservarTurno" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" @ir-a-notificaciones="vista = 'notificaciones'" />

    <MiUsuarioPaciente v-else-if="vista === 'miUsuarioPaciente'" key="miUsuarioPaciente" @ir-a-bienvenida="cerrarSesion" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-reservar-turno="irAReservarTurno()" @ir-a-profesionales="vista = 'profesionales'" @ir-a-calendario-usuario="irACalendarioUsuario()" @ir-a-notificaciones="vista = 'notificaciones'" />

    <Notificaciones v-else-if="vista === 'notificaciones'" key="notificaciones" @ir-a-bienvenida="cerrarSesion" @ir-a-principal-usuario="vista = 'principalUsuario'" @ir-a-chatbot="vista = 'chatbot'" @ir-a-reservar-turno="irAReservarTurno()" @ir-a-profesionales="vista = 'profesionales'" @ir-a-calendario-usuario="irACalendarioUsuario()" @ir-a-mi-usuario-paciente="vista = 'miUsuarioPaciente'" />
  </Transition>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
