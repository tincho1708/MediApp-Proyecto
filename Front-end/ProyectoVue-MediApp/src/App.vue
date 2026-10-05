<script setup lang="ts">
import { ref } from 'vue'
import Principal from './components/principal-medico.vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'
import MediBot from './components/MediBot.vue'
import Calendario from '@/components/calendario.vue'
import CalendarioUsuario from '@/components/calendario-usuario.vue'
import PrincipalUsuario from './components/principal-usuario.vue'
import MediPlus from './components/MediPlus.vue'
import ReservarTurno from './components/reservar-turno.vue'
import Solicitudes from './components/solicitudes.vue'
import MisPacientes from './components/mispacientes.vue'
import Disponibilidad from './components/disponibilidad.vue'
import MiUsuario from './components/MiUsuario.vue'
import { useTurnosMedico } from '@/stores/turnosMedico'

const vista = ref('bienvenida')
const { resetTurnosMedico } = useTurnosMedico()

function cerrarSesion() {
  localStorage.removeItem('sesion')
  resetTurnosMedico()
  vista.value = 'bienvenida'
}
</script>

<template>

   <Transition name="fade">
    
    <Bienvenida
      v-if="vista === 'bienvenida'"
      key="bienvenida"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-login="vista = 'iniciarSesion'"
    />


    <Registrar
      v-else-if="vista === 'registrar'"
      key="registrar"
      @ir-a-login="vista = 'iniciarSesion'"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
    />

    <IniciarSesion
      v-else-if="vista === 'iniciarSesion'"
      key="iniciarSesion"
      @bienvenida="vista = 'bienvenida'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      />

    <Principal
      v-else-if="vista === 'Principal'"
      key="principal"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <MediBot
      v-else-if="vista === 'chatbot'"
      key="chatbot"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-calendario-usuario="vista = 'calendarioUsuario'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <Calendario
      v-else-if="vista === 'calendario'"
      key="calendario"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

      <Calendario-Usuario
      v-else-if="vista === 'calendarioUsuario'"
      key="calendarioUsuario"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"/>
      
      
    <PrincipalUsuario
      v-else-if="vista === 'principalUsuario'"
      key="principalUsuario"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario-usuario="vista = 'calendarioUsuario'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"/>

    <MediPlus
      v-else-if="vista === 'MediPlus'"
      key="MediPlus"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <ReservarTurno
      v-else-if="vista === 'reservarTurno'"
      key="reservarTurno"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario-usuario="vista = 'calendarioUsuario'"/>


    <Solicitudes
      v-else-if="vista === 'solicitudes'"
      key="solicitudes"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <MisPacientes
      v-else-if="vista === 'misPacientes'"
      key="misPacientes"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <Disponibilidad
      v-else-if="vista === 'configuracion'"
      key="configuracion"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"
      @ir-a-mi-usuario="vista = 'miUsuario'"/>

    <MiUsuario
      v-else-if="vista === 'miUsuario'"
      key="miUsuario"
      @ir-a-bienvenida="cerrarSesion"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"
      @ir-a-mis-pacientes="vista = 'misPacientes'"
      @ir-a-configuracion="vista = 'configuracion'"/>
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
