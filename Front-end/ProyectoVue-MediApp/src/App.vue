<script setup lang="ts">
import { ref } from 'vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'
import medicoPaciente from './components/medico-paciente.vue'

const vista = ref('bienvenida')
</script>

<template>

   <Transition name="fade" mode="out-in">
    <Bienvenida
      v-if="vista === 'bienvenida'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-medico-paciente="vista = 'medicoPaciente'"
      @ir-a-login="vista = 'iniciarSesion'"
    />

    <medicoPaciente
      v-else-if="vista === 'medicoPaciente'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-login="vista = 'iniciarSesion'"
    />

    <Registrar
      v-else-if="vista === 'registrar'"
      @ir-a-login="vista = 'iniciarSesion'"
      @ir-a-bienvenida="vista = 'bienvenida'"
    />

    <IniciarSesion
      v-else
      @bienvenida="vista = 'bienvenida'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-medico-paciente="vista = 'medicoPaciente'"/>

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
