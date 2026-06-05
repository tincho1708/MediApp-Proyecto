<script setup lang="ts">
import { ref } from 'vue'
import Principal from './components/principal-medico.vue'
import Bienvenida from './components/bienvenida.vue'
import Registrar from './components/registrar.vue'
import IniciarSesion from './components/inicio-sesion.vue'

const vista = ref('bienvenida')
</script>

<template>

   <Transition name="fade" mode="out-in">
    
    <Bienvenida
      v-if="vista === 'bienvenida'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-login="vista = 'iniciarSesion'"
      @ir-a-principal="vista = 'Principal'"
    />

    
    <Registrar
      v-else-if="vista === 'registrar'"
      @ir-a-login="vista = 'iniciarSesion'"
      @ir-a-bienvenida="vista = 'bienvenida'"
      @ir-a-principal="vista = 'Principal'"
    />

    <IniciarSesion
      v-else-if="vista === 'iniciarSesion'"
      @bienvenida="vista = 'bienvenida'"
      @ir-a-registro="vista = 'registrar'"
      @ir-a-principal="vista = 'Principal'"
      />

    <Principal
      v-else-if ="vista === 'Principal'"
      @ir-a-bienvenida="vista = 'bienvenida'"/>

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
