
<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['ir-a-login', 'ir-a-bienvenida', 'ir-a-principal', 'ir-a-principal-usuario'])

const form = ref({
  nombre: '',
  email: '',
  password: '',
  confirmarPassword: '',
})

const tipoUsuario = ref<'Medico' | 'Paciente' | null>(null)
const error = ref('')
const cargando = ref(false)
const exito = ref('')

function seleccionar(tipo: 'Medico' | 'Paciente') {
  tipoUsuario.value = tipo
  const boton1 = document.querySelector('.boton1') as HTMLButtonElement
  const boton2 = document.querySelector('.boton2') as HTMLButtonElement
  boton1.style.transition = 'background-color 0.3s'
  boton2.style.transition = 'background-color 0.3s'
  if (tipo === 'Medico') {
    boton1.style.backgroundColor = '#4a90e2'
    boton2.style.backgroundColor = '#ccc'
  } else {
    boton1.style.backgroundColor = '#ccc'
    boton2.style.backgroundColor = '#4a90e2'
  }
}

async function testearSubmit() {
  error.value = ''
  if (!tipoUsuario.value) {
    error.value = 'Seleccioná un tipo de usuario (Médico o Paciente)'
    return
  }
  if (form.value.password !== form.value.confirmarPassword) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  cargando.value = true
  const url = tipoUsuario.value === 'Medico' || tipoUsuario.value === 'Paciente'
    ? '/auth/medicos/registro'
    : '/auth/pacientes/registro'

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: form.value.nombre, mail: form.value.email, password: form.value.password }),
    })
    const data = await res.json()

    if (res.ok && tipoUsuario.value === 'Paciente') {
      exito.value = data.message
      emit('ir-a-principal-usuario')

    }
    else if (res.ok && tipoUsuario.value === 'Medico') {
      exito.value = data.message
      emit('ir-a-principal')

    } else {
      error.value = data.detail || 'Error al registrarse'
    }
  } catch {
    error.value = 'No se pudo conectar al servidor'
  } finally {
    cargando.value = false
  }
}
</script>



<template>
  <div>
  <button class="boton-atras" @click="emit('ir-a-bienvenida')"> <svg xmlns="http://www.w3.org/2000/svg" width="18" height="15" viewBox="0 0 18 15" fill="none">
    <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black"/>
    </svg> Atrás
  </button>
  <div class="titulo">Crear cuenta</div>

  <div class="contenedor">

    <div class="tipo-usuario">
      <button class="boton1"@click="seleccionar('Medico')">Medico</button>
      <div class="separador"></div>
      <button class="boton2"@click="seleccionar('Paciente')">Paciente</button>
    </div>
  <div>
    <form autocomplete="off" @submit.prevent="testearSubmit">
      <div class="campo">
        <input id="nombre" v-model="form.nombre" type="text" placeholder="Nombre" required />
      </div>

      <div class="campo">
        <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
      </div>

      <div class="campo">
        <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
      </div>

      <div class="campo">
        <input id="confirmar" v-model="form.confirmarPassword" type="password" placeholder="Repite tu contraseña" required />
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="exito" class="exito">{{ exito }}</p>

      <button v-if="!exito" class="submit" type="submit" :disabled="cargando">
        {{ cargando ? 'Creando cuenta...' : 'Crear cuenta' }}
      </button>
      <button v-if="exito" class="submit" type="button" @click="emit('ir-a-login')">Ir a iniciar sesión</button>

      <p class="login-link">¿Ya tienes cuenta? <a href="#" class="underline" @click.prevent="emit('ir-a-login')">Inicia sesión</a></p>
    </form>

    
  </div>
  </div>
  </div>
</template>


<style scoped>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.titulo {
  color: #000;
  text-align: center;
  font-family: 'Inter', 'sans-serif';
  font-size: 3.5rem;
  font-weight: 400;
  line-height: normal;
  text-align: center;
  margin-bottom: 0;
}

.boton-atras {
  color: #000;
  font-family: 'Inter', 'sans-serif';
  font-size: 1.25rem;
  font-weight: 400;
  line-height: normal;
  margin: 1.25rem;
  cursor: pointer;
  width: 11.125rem;
  height: 4rem;
  border-radius: 1.875rem;
  background: #2E9CE0;
  border: none;
  display: flex;
  align-items: center;
  padding-left: 2.5%;
  justify-content: flex-start;
  gap: 10%;
}
.boton-atras.svg {
  stroke-width: 0.125rem;
  stroke: #000;
  width: 1.007813rem;
  height: 0;
}

.tipo-usuario {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}

.separador {
  width: 0.125rem;
  height: 2.25rem;
  background: #000;
  margin: 0 0.5rem;
}

.boton1, .boton2 {
  font-family: 'Inter', sans-serif;
  background-color: #D9D9D9;
  border: none;
  width: 12.5rem;
  height: 3.125rem;
  font-size: 1.5625rem;
  cursor: pointer;
  border-radius: 2.5rem;
  color: #000000;
}

boton1.activo, .boton2.activo {
  background-color: #4a90e2;
  color: #fff;
}

.contenedor {
  max-width: 30rem;
  width: 90%;
  margin: 0.75rem auto;
  padding: 2rem;
  border: 0.0625rem solid #ccc;
  border-radius: 1.8125rem;
  background-color: #FFFFFF;
  overflow: hidden;
  box-shadow: 0 0.0625rem 1.85625rem 0.6875rem rgba(0, 0, 0, 0.25);
}

form {
  width: 100%;
}


.campo {
  font-family: 'Inter', sans-serif;
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
  border-radius: 2.75rem;
  border: 0.125rem solid #000; 
  font-size: 1rem;
  width: 100%;
  min-width: 0;
}

input:focus {
  outline: 0.125rem solid #4a90e2;
  border-color: transparent;
}

.submit {
  width: 100%;
  padding: 0.65rem;
  margin-top: 0.5rem;
  background: #4a90e2;
  color: black;
  border: none;
  border-radius: 1.25rem;
  font-size: 1.5rem;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  height: 3.125rem;
}

button:hover {
  background: #357abd;
}

.error {
  color: red;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.exito {
  color: #2e7d32;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 1rem;
}


</style>
