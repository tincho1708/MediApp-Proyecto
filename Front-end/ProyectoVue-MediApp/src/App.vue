<script setup lang="ts">
import { ref } from 'vue'
import Principal from './components/principal-medico.vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'
import Chatbot from './components/chatbot.vue'
import CalendarioMedico from './components/calendario-medico.vue'
import PrincipalUsuario from './components/principal-usuario.vue'

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
      @ir-a-calendario="vista = 'calendarioMedico'"/>

    <Chatbot
      v-else-if="vista === 'chatbot'"
      key="chatbot"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"/>

    <CalendarioMedico
      v-else-if="vista === 'calendarioMedico'"
      key="calendarioMedico"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"
      @ir-a-principal-usuario="vista = 'principalUsuario'"/>
      
    <PrincipalUsuario
      v-else-if="vista === 'principalUsuario'"
      key="principalUsuario"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
      @ir-a-chatbot="vista = 'chatbot'"/>
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
