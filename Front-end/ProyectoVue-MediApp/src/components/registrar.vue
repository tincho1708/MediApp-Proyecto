<!-- JavaScript -->

<script setup lang="ts">

import { ref } from 'vue'

const form = ref({
  nombre: '',
  apellido: '',
  email: '',
  telefono: '',
  password: '',
  confirmarPassword: '',
})

const error = ref('')
const exito = ref(false)

function validar(): boolean {
  if (!form.value.nombre || !form.value.apellido || !form.value.email || !form.value.password) {
    error.value = 'Por favor completa todos los campos obligatorios.'
    return false
  }
  if (form.value.password !== form.value.confirmarPassword) {
    error.value = 'Las contraseñas no coinciden.'
    return false
  }
  if (form.value.password.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return false
  }
  return true
}

function registrar() {
  error.value = ''
  if (!validar()) return
  exito.value = true
}

</script>


<!-- HTML -->

<template>
  <div class="contenedor">
    <h1>Crear cuenta</h1>

    <form v-if="!exito" @submit.prevent="registrar">
      <div class="fila-doble">
        <div class="campo">
          <label for="nombre">Nombre *</label>
          <input id="nombre" v-model="form.nombre" type="text" placeholder="Juan" required />
        </div>
        <div class="campo">
          <label for="apellido">Apellido *</label>
          <input id="apellido" v-model="form.apellido" type="text" placeholder="Pérez" required />
        </div>
      </div>

      <div class="campo">
        <label for="email">Correo electrónico *</label>
        <input id="email" v-model="form.email" type="email" placeholder="juan@ejemplo.com" required />
      </div>

      <div class="campo">
        <label for="telefono">Teléfono</label>
        <input id="telefono" v-model="form.telefono" type="tel" placeholder="+54 11 1234-5678" />
      </div>

      <div class="campo">
        <label for="password">Contraseña *</label>
        <input id="password" v-model="form.password" type="password" placeholder="Mínimo 8 caracteres" required />
      </div>

      <div class="campo">
        <label for="confirmar">Confirmar contraseña *</label>
        <input id="confirmar" v-model="form.confirmarPassword" type="password" placeholder="Repite tu contraseña" required />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit">Registrarse</button>

      <p class="login-link">¿Ya tienes cuenta? <a href="#">Inicia sesión</a></p>
    </form>

    <div v-else class="exito">
      <p>Cuenta creada correctamente. ¡Bienvenido, {{ form.nombre }}!</p>
    </div>
  </div>
</template>

<!-- CSS -->

<style scoped>


.contenedor {
  max-width: 480px;
  margin: 60px auto;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}

h1 {
  margin-bottom: 1.5rem;
  font-size: 1.6rem;
}

.fila-doble {
  display: flex;
  gap: 1rem;
}

.fila-doble .campo {
  flex: 1;
}

.campo {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
}

input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #bbb;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: 2px solid #4a90e2;
  border-color: transparent;
}

button {
  width: 100%;
  padding: 0.65rem;
  margin-top: 0.5rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  background: #357abd;
}

.error {
  color: red;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.exito {
  color: green;
  font-size: 1rem;
}


</style>
