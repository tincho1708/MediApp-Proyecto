<script setup lang="ts">
import { ref } from 'vue'
import Principal from './components/principal-medico.vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'
import Chatbot from './components/chatbot.vue'
import Calendario from '@/components/calendario.vue'
import CalendarioUsuario from '@/components/calendario-usuario.vue'
import PrincipalUsuario from './components/principal-usuario.vue'
import MediPlus from './components/MediPlus.vue'
import ReservarTurno from './components/reservar-turno.vue'
import Solicitudes from './components/solicitudes.vue'

const vista = ref('bienvenida')
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
      @ir-a-bienvenida="vista = 'bienvenida'"
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
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"/>

    <Chatbot
      v-else-if="vista === 'chatbot'"
      key="chatbot"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"
      @ir-a-solicitudes="vista = 'solicitudes'"/>

    <Calendario
      v-else-if="vista === 'calendario'"
      key="calendario"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-MediPlus="vista = 'MediPlus'"
      @ir-a-solicitudes="vista = 'solicitudes'"/>

      <Calendario-Usuario
      v-else-if="vista === 'calendarioUsuario'"
      key="calendarioUsuario"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"/>
      
      
    <PrincipalUsuario
      v-else-if="vista === 'principalUsuario'"
      key="principalUsuario"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario-usuario="vista = 'calendarioUsuario'"
      @ir-a-reservar-turno="vista = 'reservarTurno'"/>

    <MediPlus
      v-else-if="vista === 'MediPlus'"
      key="MediPlus"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-solicitudes="vista = 'solicitudes'"/>

    <ReservarTurno
      v-else-if="vista === 'reservarTurno'"
      key="reservarTurno"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario-usuario="vista = 'calendarioUsuario'"/>


    <Solicitudes
      v-else-if="vista === 'solicitudes'"
      key="solicitudes"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-calendario="vista = 'calendario'"
      @ir-a-MediPlus="vista = 'MediPlus'"/>
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
