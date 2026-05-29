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
  <button class="boton-atras" @click="emit('bienvenida')"> <svg xmlns="http://www.w3.org/2000/svg" width="18" height="15" viewBox="0 0 18 15" fill="none">
    <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black"/>
    </svg> Atrás
  </button>

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

    <p class="separador">──────────────── O ────────────────</p>
    <form autocomplete="off" @submit.prevent="emit('ir-a-principal')">
      <div class="campo">
        <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
      </div>

      <div class="campo">
        <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
      </div>
      <p class="olvido-contraseña">¿Olvidaste tu contraseña? <a href="h">Recuperala</a></p>

      <button class="iniciar" type="submit" @click="emit('ir-a-principal')">Iniciar sesión</button>

      <p class="registro-link">¿No tenés cuenta? <a href="#" @click.prevent="emit('ir-a-registro')">Registrate</a></p>
    </form>
  </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.boton-atras {
  color: #000;
  font-family: 'Lexend', 'sans-serif';
  font-size: 20px;
  font-weight: 400;
  line-height: normal;
  margin: 20px;
  cursor: pointer;
  width: 178px;
  height: 64px;
  border-radius: 30px;
  background: #2E9CE0;
  border: none;
}
.boton-atras.svg {
  stroke-width: 2px;
  stroke: #000;
  width: 16.125px;
  height: 0;
}
.contenedor {
  margin: 30px auto;
  margin-top: 0;
  padding: 32px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 1px 29.7px 11px rgba(0, 0, 0, 0.13);
  width: 450px;
  height: 540px;
  align-items: center;
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
  margin-bottom: 20px;
  }

input {
  padding: 10px 15px;
  border: 1px solid black;
  border-radius: 4px;
  font-size: 16px;
}

input:focus {
  outline: 2px solid #4a90e2;
  border-color: transparent;
}

.iniciar {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  background: #4a90e2;
  color: black;
  border: none;
  border-radius: 30px;
  font-size: 35px;
  cursor: pointer;
  font-weight: 400;
  font-family: 'Lexend', sans-serif;
  height: 80px;
}

button:hover {
  background: #3CA4D6;
}

.error {
  color: red;
  font-size: 13px;
  margin-bottom: 8px;
}

.registro-link {
  margin-top: 16px;
  text-align: center;
  font-size: 15px;
  gap: 20px;
}
.olvido-contraseña {
  font-size: 15px;
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
  width: 100%;
  margin-left: 0;
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
  background-color: #7cb1f192;
}

.separador {
  color: black;
  text-align: center;
  margin-bottom: 10px;
  font-size: 15.7px;
}
</style>
