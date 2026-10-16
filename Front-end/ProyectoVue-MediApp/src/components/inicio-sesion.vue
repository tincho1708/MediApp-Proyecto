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
  <div class="pagina">
  <div class="contenedor">
    <button class="boton-atras" @click="emit('bienvenida')">
      <svg style="width:1.125rem; height:0.9375rem;" viewBox="0 0 18 15" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black"/>
      </svg>
      Volver atrás
    </button>

    <div class="titulo">Iniciar sesión</div>
    <div class="subtitulo">Ingresa tus datos para acceder a tu cuenta.</div>

    <div class="etiqueta-tipo">O inicia sesión con</div>
    <div class="social-fila">
      <button type="button" class="social-boton">
        <img src="@/assets/imagenes/google.png" alt="Google"/>
        Continuar con Google
      </button>
      <button type="button" class="social-boton">
        <img src="@/assets/imagenes/microsoft.png" alt="Microsoft"/>
        Continuar con Microsoft
      </button>
    </div>

    <div class="separador"><span>O</span></div>

    <form autocomplete="off" @submit.prevent="testearSubmit">
      <div class="campo">
        <svg style="width:1.125rem; height:1.125rem;" class="icono-campo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/></svg>
        <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
      </div>

      <div class="campo">
        <svg style="width:1.125rem; height:1.125rem;" class="icono-campo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="submit" type="submit" :disabled="cargando">
        {{ cargando ? 'Iniciando...' : 'Iniciar sesión' }}
      </button>

      <p class="enlace"><a href="#" class="underline" @click.prevent>¿Olvidaste tu contraseña?</a></p>
      <p class="enlace">¿No tenés cuenta? <a href="#" class="underline" @click.prevent="emit('ir-a-registro')">Registrate</a></p>
    </form>
  </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.pagina {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', sans-serif;
}

.contenedor {
  max-width: 34rem;
  width: 90%;
  margin: 2rem auto;
  padding: 2rem 2.25rem;
  border-radius: 1.5rem;
  background-color: #FFFFFF;
  box-shadow: 0 0.0625rem 1.85625rem 0.6875rem rgba(0, 0, 0, 0.08);
}

.boton-atras {
  color: #000;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  background: #F1F4F7;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  transition: background-color 0.2s ease;
}

.boton-atras:hover {
  background-color: #E4EAF0;
}

.titulo {
  color: #0F172A;
  font-family: 'Inter', sans-serif;
  font-size: 2.25rem;
  font-weight: 700;
  line-height: normal;
  margin-bottom: 0.375rem;
}

.subtitulo {
  color: #6B7280;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.etiqueta-tipo {
  color: #6B7280;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.social-fila {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.social-boton {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #111827;
  background-color: #FFFFFF;
  border: 0.0625rem solid #D1D5DB;
  border-radius: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.social-boton:hover {
  background-color: #F9FAFB;
}

.social-boton img {
  width: 1.25rem;
  height: 1.25rem;
  object-fit: contain;
}

.separador {
  display: flex;
  align-items: center;
  text-align: center;
  color: #9CA3AF;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.separador::before,
.separador::after {
  content: '';
  flex: 1;
  border-bottom: 0.0625rem solid #D1D5DB;
}

.separador span {
  padding: 0 0.75rem;
}

form {
  width: 100%;
}

.campo {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.icono-campo {
  position: absolute;
  left: 1rem;
  color: #9CA3AF;
  pointer-events: none;
}

input {
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  border-radius: 0.875rem;
  border: 0.0625rem solid #D1D5DB;
  background-color: #F9FAFB;
  font-size: 1rem;
  width: 100%;
  min-width: 0;
  font-family: 'Inter', sans-serif;
}

input:focus {
  outline: 0.125rem solid #4a90e2;
  border-color: transparent;
}

.submit {
  width: 100%;
  padding: 0.875rem;
  margin-top: 1.5rem;
  background: linear-gradient(90deg, #6AA6F2 0%, #3D6FC2 100%);
  color: white;
  border: none;
  border-radius: 1rem;
  font-size: 1.125rem;
  font-weight: 700;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  height: auto;
}

.submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #DC2626;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.enlace {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.95rem;
}

.enlace a {
  color: #2563EB;
  font-weight: 500;
}
</style>
