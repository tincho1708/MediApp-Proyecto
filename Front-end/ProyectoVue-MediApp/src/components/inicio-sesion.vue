<script setup lang="ts">
import { ref } from 'vue'
import { useTurnosMedico } from '@/stores/turnosMedico'

const emit = defineEmits(['ir-a-registro', 'bienvenida', 'ir-a-principal', 'ir-a-principal-usuario'])

const { resetTurnosMedico } = useTurnosMedico()

const form = ref({
  email: '',
  password: '',
})

const error = ref('')
const cargando = ref(false)

async function testearSubmit() {
  error.value = ''
  cargando.value = true

  const body = { mail: form.value.email, password: form.value.password }
  const intentos = [
    { url: '/auth/medicos/login', tipo: 'Medico' },
    { url: '/auth/pacientes/login', tipo: 'Paciente' },
  ]

  for (const { url, tipo } of intentos) {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()

      if (res.ok && tipo === 'Medico') {
        localStorage.setItem('sesion', JSON.stringify({ token: data.access_token, tipo, email: form.value.email, nombre: data.nombre }))
        resetTurnosMedico()
        emit('ir-a-principal')
        return
      }
      if (res.ok && tipo === 'Paciente') {
        localStorage.setItem('sesion', JSON.stringify({ token: data.access_token, tipo, email: form.value.email, nombre: data.nombre }))
        resetTurnosMedico()
        emit('ir-a-principal-usuario')
        return
      }
      if (res.status === 403) {
        error.value = data.detail
        cargando.value = false
        return
      }
      
    } catch {
      error.value = 'No se pudo conectar al servidor'
      cargando.value = false
      return
    }
  }

  error.value = 'Credenciales incorrectas'
  cargando.value = false
}
</script>

<template>
  <div>
  <button class="boton-atras" @click="emit('bienvenida')"> <svg xmlns="http://www.w3.org/2000/svg" width="18" height="15" viewBox="0 0 18 15" fill="none">
    <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black"/>
    </svg> Atrás
  </button>

  <div class="contenedor">
    <h1>Iniciar sesión</h1>

    <button class="texto-sesion1">
    <img src="@/assets/imagenes/google.png" alt="Google"/>
    Continuar con Google
    </button> 

    <button class="texto-sesion2">
    <img src="@/assets/imagenes/microsoft.png" alt="Microsoft"/>
    Continuar con Microsoft
    </button>

    <p class="separador">──────────────── O ────────────────</p>
    <form autocomplete="off" @submit.prevent="testearSubmit">
      <div class="campo">
        <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
      </div>

      <div class="campo">
        <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
      </div>
      <p class="olvido-contraseña">¿Olvidaste tu contraseña? <a href="h" class="underline">Recuperala</a></p>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="iniciar" type="submit" :disabled="cargando">
        {{ cargando ? 'Iniciando...' : 'Iniciar sesión' }}
      </button>

      <p class="registro-link">¿No tenés cuenta? <a href="h"  class="underline" @click.prevent="emit('ir-a-registro')">Registrate</a></p>
    </form>
  </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.boton-atras {
  color: #000;
  font-family: 'Inter', 'sans-serif';
  font-size: 1.0625rem;
  font-weight: 500;
  line-height: normal;
  margin: 1.25rem;
  cursor: pointer;
  width: auto;
  height: auto;
  padding: 0.5rem 0.875rem;
  border-radius: 0.75rem;
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
}

.boton-atras:hover {
  background-color: #EAF4FC;
}

.boton-atras.svg {
  stroke-width: 0.125rem;
  stroke: #000;
  width: 1.007813rem;
  height: 0;
}
.contenedor {
  margin: 1.875rem auto;
  margin-top: 0;
  padding: 2rem;
  border: 0.0625rem solid #ccc;
  border-radius: 0.5rem;
  background-color: white;
  box-shadow: 0 0.0625rem 1.85625rem 0.6875rem rgba(0, 0, 0, 0.13);
  width: 28.125rem;
  height: 33.75rem;
  align-items: center;
}

h1 {
  font-family: 'Inter';
  font-weight: 400;
  margin-bottom: 1.125rem;
  font-size: 2.5rem;
  text-align: center;
  line-height: normal;
}

.campo {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.25rem;
  }

input {
  padding: 0.625rem 0.9375rem;
  border: 0.0625rem solid black;
  border-radius: 0.25rem;
  font-size: 1rem;
}

input:focus {
  outline: 0.125rem solid #4a90e2;
  border-color: transparent;
}

.iniciar {
  width: 100%;
  padding: 0.625rem;
  margin-top: 0.5rem;
  background: #4a90e2;
  color: black;
  border: none;
  border-radius: 1.875rem;
  font-size: 2.1875rem;
  cursor: pointer;
  font-weight: 400;
  font-family: 'Inter', sans-serif;
  height: 5rem;
}

button:hover {
  background: #3CA4D6;
}

.error {
  color: red;
  font-size: 0.8125rem;
  margin-bottom: 0.5rem;
}

.registro-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9375rem;
  gap: 1.25rem;
}
.olvido-contraseña {
  font-size: 0.9375rem;
}

.texto-sesion1, .texto-sesion2 {
  font-family: 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 200;
  color: #000000;
  cursor: pointer;
  border: 0.09375rem solid #000000;
  border-radius: 2.5rem;
  padding: 0.1875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3125rem;
  margin: 0.625rem;
  background-color: transparent;
  width: 100%;
  margin-left: 0;
}

.texto-sesion1 img {
  width: 2.1875rem;
  height: 2.1875rem;
  object-fit: contain;
  mix-blend-mode: multiply;
}
.texto-sesion2 img {
  width: 1.75rem;
  height: 1.75rem;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion1:hover, .texto-sesion2:hover {
  background-color: #7cb1f192;
}

.texto-sesion1:focus, .texto-sesion2:focus {
  outline: none;
}

.separador {
  color: black;
  text-align: center;
  margin-bottom: 0.625rem;
  font-size: 0.98125rem;
}
</style>
