<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['ir-a-registro', 'bienvenida','ir-a-principal'])

const form = ref({
  email: '',
  password: '',
})




</script>

<template>
  <div>
  <button class="btn-atras" @click="emit('bienvenida')">← Atrás</button>

  <div class="contenedor">
    <h1>Iniciar sesión</h1>

    <button class="texto-sesion1" @click="emit('ir-a-principal')">
    <img src="@/assets/imagenes/google.png" alt="Google"/>
    Continuar con Google
    </button> 

    <button class="texto-sesion2" @click="emit('ir-a-principal')">
    <img src="@/assets/imagenes/microsoft.png" alt="Microsoft"/>
    Continuar con Microsoft
    </button>

    <p class="separador">────────────── O ──────────────</p>
    <form autocomplete="off" @submit.prevent="emit('ir-a-principal')">
      <div class="campo">
        <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
      </div>

      <div class="campo">
        <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
      </div>
      <p class="olvido-contraseña">¿Olvidaste tu contraseña? <a href="h">Recuperala</a></p>

      <button type="submit" @click="emit('ir-a-principal')">Iniciar sesión</button>

      <p class="registro-link">¿No tenés cuenta? <a href="#" @click.prevent="emit('ir-a-registro')">Registrate</a></p>
    </form>
  </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.btn-atras {
  font-family: 'Lexend', sans-serif;
  margin: 20px;
  background: none;
  border: none;
  width: 100px;
  background-color: #bbb;
  font-size: 16px;
  cursor: pointer;
}
.contenedor {
  max-width: 400px;
  margin: 60px auto;
  padding: 32px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 1px 29.7px 11px rgba(0, 0, 0, 0.13);
}

h1 {
  font-family: 'Lexend';
  font-weight: 100;
  margin-bottom: 18px;
  font-size: 40px;
  text-align: center;
  line-height: normal;
}

.campo {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
  }

input {
  padding: 8px 12px;
  border: 1px solid black;
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
  color: black;
  border: none;
  border-radius: 4px;
  font-size: 20px;
  cursor: pointer;
  font-weight: 400;
  font-family: 'Lexend', sans-serif;
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
  font-size: 13px;
}

.texto-sesion1, .texto-sesion2 {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 200;
  color: #000000;
  cursor: pointer;
  border: 1.5px solid #000000;
  border-radius: 40px;
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin: 10px;
  background-color: transparent;
}

.texto-sesion1 img {
  width: 35px;
  height: 35px;
  object-fit: contain;
  mix-blend-mode: multiply;
}
.texto-sesion2 img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion1:hover, .texto-sesion2:hover {
  background-color: #00b7ff48;
}

.separador {
  color: black;
  text-align: center;
  margin-bottom: 10px;
  font-size: 15.7px;
}
</style>
