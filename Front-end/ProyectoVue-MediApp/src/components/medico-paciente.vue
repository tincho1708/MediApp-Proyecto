<script setup lang="ts">

import { ref } from 'vue'

const emit = defineEmits(['ir-a-registro'])
const tipoUsuario = ref('')

function seleccionar(tipo: string) {
  tipoUsuario.value = tipo
  emit('ir-a-registro')
}

</script>

<template>

  <div class="contenedor">
    <div class="contenedor1">Registrarse como:
      <button @click="seleccionar('medico')" class="contenedor-1">Medico</button>
      <button @click="seleccionar('paciente')" class="contenedor-2">Paciente</button>
    </div>
  </div>
</template>

<style lang="css" scoped>

@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.contenedor {
  font-family: 'Lexend', sans-serif;
  max-width: 400px;
  margin: 60px auto;
  padding: 32px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #D9D9D9;
}
.contenedor1 {
  margin-bottom: 24px;
  font-size: 50px;
  align-items: center;
  display: flex;
  flex-direction: column;
}

.contenedor-1 {
  font-family: 'Lexend', sans-serif;
  width: 100%;
  height: 80px;
  padding: 10px;
  margin-top: 8px;
  background: #999999;
  color: white;
  border: none;
  border-radius: 44px;
  font-size: 35px;
  cursor: pointer;
  align-items: center;
  margin: 20px;
}

.contenedor button:hover {
  background: #357abd;
}

.contenedor-2 {
  font-family: 'Lexend', sans-serif;
  width: 100%;
  height: 80px;
  padding: 10px;
  margin-top: 8px;
  background: #5B5A5A;
  color: white;
  border: none;
  border-radius: 44px;
  font-size: 35px;
  cursor: pointer;
  align-items: center;
  margin: 20px;
}
.contenedor-2 button:hover {
  background: #357abd;
}
</style>