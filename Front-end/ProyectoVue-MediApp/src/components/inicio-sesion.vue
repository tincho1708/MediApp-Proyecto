<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['ir-a-registro'])

const form = ref({
  email: '',
  password: '',
})

const error = ref('')

function iniciarSesion() {
  error.value = ''
  if (!form.value.email || !form.value.password) {
    error.value = 'Por favor completá todos los campos.'
    return
  }
}
</script>

<template>
  <div class="contenedor">
    <h1>Iniciar sesión</h1>

    <form @submit.prevent="iniciarSesion" autocomplete="off">
      <div class="campo">
        <label for="email">Correo electrónico</label>
        <input id="email" v-model="form.email" type="email" placeholder="juan@ejemplo.com" required />
      </div>

      <div class="campo">
        <label for="password">Contraseña</label>
        <input id="password" v-model="form.password" type="password" placeholder="Tu contraseña" required />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit">Iniciar sesión</button>

      <p class="registro-link">¿No tenés cuenta? <a href="#" @click.prevent="emit('ir-a-registro')">Registrate</a></p>
      <p class="olvido-contraseña">¿Olvidaste tu contraseña? <a href="h">Recuperala</a></p>
    </form>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.contenedor {
  max-width: 400px;
  margin: 60px auto;
  padding: 32px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

h1 {
  font-family: 'Lexend', sans-serif;
  margin-bottom: 24px;
  font-size: 25.6px;
}

.campo {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

label {
  font-family: 'Lexend', sans-serif;
  margin-bottom: 5px;
  font-size: 14px;
}

input {
  padding: 8px 12px;
  border: 1px solid #bbb;
  border-radius: 4px;
  font-size: 16px;
}

input:focus {
  outline: 2px solid #4a90e2;
  border-color: transparent;
}

button {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background: #357abd;
}

.error {
  color: red;
  font-size: 13px;
  margin-bottom: 8px;
}

.registro-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
}
.olvido-contraseña {
  margin-top: 6px;
  text-align: center;
  font-size: 14px;
}
</style>
