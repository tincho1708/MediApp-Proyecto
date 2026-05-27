
<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['ir-a-login', 'ir-a-bienvenida', 'ir-a-principal'])

const form = ref({
  nombre: '',
  email: '',
  telefono: '',
  password: '',
  confirmarPassword: '',
})

const exito = ref(false)
function seleccionar(tipo: 'Medico' | 'Paciente') {
  const boton1 = document.querySelector('.boton1') as HTMLButtonElement
  const boton2 = document.querySelector('.boton2') as HTMLButtonElement

  boton1.style.transition = 'background-color 0.3s'
  boton2.style.transition = 'background-color 0.3s'

  if (tipo === 'Medico') {
    boton1.style.backgroundColor = '#4a90e2'
    boton2.style.backgroundColor = '#ccc'
    console.log(tipo);
  } else {
    boton1.style.backgroundColor = '#ccc'
    boton2.style.backgroundColor = '#4a90e2'
    console.log(tipo);
  }
}
</script>



<template>
  <div>
  <button class="btn-atras" @click="emit('ir-a-bienvenida')">← Atrás</button>
  <div class="titulo">Crear cuenta</div>
  <div class="contenedor">

    <div class="tipo-usuario">
      <button class="boton1"@click="seleccionar('Medico')">Medico</button>
      <div class="separador"></div>
      <button class="boton2"@click="seleccionar('Paciente')">Paciente</button>
    </div>

    <form v-if="!exito" autocomplete="off" @submit.prevent="emit('ir-a-principal')">
      
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


      <button class="submit" type="submit" @click="emit('ir-a-principal')">Crear cuenta</button>

      <p class="login-link">¿Ya tienes cuenta? <a href="#" @click.prevent="emit('ir-a-login')">Inicia sesión</a></p>
    </form>

    
  </div>
  </div>
</template>


<style scoped>

@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.titulo {
  font-family: 'Lexend', sans-serif;
  font-size: 40px;
  text-align: center;
  margin-bottom: 0;
}

.btn-atras {
  font-family: 'Lexend', sans-serif;
  margin: 20px;
  padding: 10px;
  background: none;
  border: none;
  width: 100px;
  background-color: #bbb;
  font-size: 16px;
  cursor: pointer;
  border-radius: 7px;
}

.tipo-usuario {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
}

.separador {
  width: 2px;
  height: 36px;
  background: #000;
  margin: 0 8px;
}

.boton1, .boton2 {
  font-family: 'Lexend', sans-serif;
  background-color: #bbb;
  border: none;
  width: 200px;
  height: 50px;
  font-size: 25px;
  cursor: pointer;
  border-radius: 40px;
  color: #000000;
}

boton1.activo, .boton2.activo {
  background-color: #4a90e2;
  color: #fff;
}

.contenedor {
  max-width: 480px;
  width: 90%;
  margin: 12px auto;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #FFFFFF;
  overflow: hidden;
  box-shadow: 0 1px 29.7px 11px rgba(0, 0, 0, 0.25);
}

form {
  width: 100%;
}


.campo {
  font-family: 'Lexend', sans-serif;
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

label {
  margin-bottom: 4.8px;
  font-size: 14.4px;
}

input {
  padding: 8px 12px;
  border-radius: 44px;
  border: 1.5px solid #000;
  font-size: 16px;
  width: 100%;
  min-width: 0;
}

input:focus {
  outline: 2px solid #4a90e2;
  border-color: transparent;
}

.submit {
  width: 100%;
  padding: 10.4px;
  margin-top: 8px;
  background: #4a90e2;
  color: black;
  border: none;
  border-radius: 20px;
  font-size: 24px;
  cursor: pointer;
  height: 50px;
}

button:hover {
  background: #357abd;
}

.error {
  color: red;
  font-size: 13.6px;
  margin-bottom: 8px;
}

.login-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14.4px;
}


</style>
