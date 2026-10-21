<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits([
  'ir-a-login',
  'ir-a-bienvenida',
  'ir-a-principal',
  'ir-a-principal-usuario',
])

const form = ref({
  nombre: '',
  email: '',
  password: '',
})

const tipoUsuario = ref<'Medico' | 'Paciente' | null>(null)
const error = ref('')
const cargando = ref(false)
const exito = ref('')

function seleccionar(tipo: 'Medico' | 'Paciente') {
  tipoUsuario.value = tipo
}

type Especialidad = { id_especialidad: number; nombre_especialidad: string }

const paso = ref<1 | 2>(1)
const medicoId = ref<number | null>(null)
const setupToken = ref('')

const especialidades = ref<Especialidad[]>([])
const cargandoEspecialidades = ref(false)
const errorEspecialidades = ref('')
const busquedaEspecialidad = ref('')
const especialidadesSeleccionadas = ref<number[]>([])
const MAX_ESPECIALIDADES = 3

const especialidadesFiltradas = computed(() => {
  const q = busquedaEspecialidad.value.trim().toLowerCase()
  if (!q) return especialidades.value
  return especialidades.value.filter((e) => e.nombre_especialidad.toLowerCase().includes(q))
})

async function cargarEspecialidades() {
  cargandoEspecialidades.value = true
  errorEspecialidades.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/especialidades`)
    if (!res.ok) throw new Error()
    especialidades.value = await res.json()
  } catch {
    errorEspecialidades.value =
      'No se pudieron cargar las especialidades. Intentá de nuevo más tarde.'
  } finally {
    cargandoEspecialidades.value = false
  }
}

function toggleEspecialidad(id: number) {
  const i = especialidadesSeleccionadas.value.indexOf(id)
  if (i !== -1) {
    especialidadesSeleccionadas.value.splice(i, 1)
    return
  }
  if (especialidadesSeleccionadas.value.length >= MAX_ESPECIALIDADES) return
  especialidadesSeleccionadas.value.push(id)
}

async function confirmarEspecialidades() {
  if (!especialidadesSeleccionadas.value.length || !medicoId.value) return
  cargando.value = true
  errorEspecialidades.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/medicos/setup-especialidades`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        setup_token: setupToken.value,
        especialidad_ids: especialidadesSeleccionadas.value,
      }),
    })
    const data = await res.json()
    if (!res.ok) {
      errorEspecialidades.value = data.detail || 'No se pudieron guardar las especialidades.'
      return
    }
    emit('ir-a-login')
  } catch {
    errorEspecialidades.value = 'No se pudo conectar al servidor.'
  } finally {
    cargando.value = false
  }
}

async function testearSubmit() {
  error.value = ''
  if (!tipoUsuario.value) {
    error.value = 'Seleccioná un tipo de usuario (Médico o Usuario)'
    return
  }

  cargando.value = true
  const url = tipoUsuario.value === 'Medico' ? '/auth/medicos/registro' : '/auth/pacientes/registro'

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre: form.value.nombre,
        mail: form.value.email,
        password: form.value.password,
      }),
    })
    const data = await res.json()

    if (res.ok && tipoUsuario.value === 'Paciente') {
      exito.value = data.message
      emit('ir-a-principal-usuario')
    } else if (res.ok && tipoUsuario.value === 'Medico') {
      medicoId.value = data.medico_id
      setupToken.value = data.setup_token
      paso.value = 2
      cargarEspecialidades()
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
  <div class="pagina">
    <div class="contenedor" v-if="paso === 1">
      <button class="boton-atras" @click="emit('ir-a-bienvenida')">
        <svg style="width: 1.125rem; height: 0.9375rem" viewBox="0 0 18 15" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black" />
        </svg>
        Volver atrás
      </button>

      <div class="titulo">Crear cuenta</div>
      <div class="subtitulo">Completá tus datos para crear tu cuenta.</div>

      <div class="etiqueta-tipo">Registrarse como</div>
      <div class="tipo-usuario">
        <button type="button" class="tipo-boton" :class="{ activo: tipoUsuario === 'Medico' }" @click="seleccionar('Medico')">
          Médico
        </button>
        <button type="button" class="tipo-boton" :class="{ activo: tipoUsuario === 'Paciente' }" @click="seleccionar('Paciente')">
          Paciente
        </button>
      </div>

      <form autocomplete="off" @submit.prevent="testearSubmit">
        <div class="campo">
          <svg style="width: 1.125rem; height: 1.125rem" class="icono-campo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          <input id="nombre" v-model="form.nombre" type="text" placeholder="Nombre completo" required />
        </div>

        <div class="campo">
          <svg style="width: 1.125rem; height: 1.125rem" class="icono-campo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="m22 6-10 7L2 6" />
          </svg>
          <input id="email" v-model="form.email" type="email" placeholder="Correo electrónico" required />
        </div>

        <div class="campo">
          <svg style="width: 1.125rem; height: 1.125rem" class="icono-campo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke->
            <rect x="3" y="11" width="18" height="11" rx="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <input id="password" v-model="form.password" type="password" placeholder="Contraseña" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="submit" type="submit" :disabled="cargando">
          {{ cargando ? 'Creando cuenta...' : 'Crear cuenta' }}
        </button>

        <p class="login-link">
          ¿Ya tenés cuenta?
          <a href="#" class="underline" @click.prevent="emit('ir-a-login')">Iniciar sesión</a>
        </p>
      </form>
    </div>

    <div class="contenedor-especialidad" v-else>
      <button class="boton-atras-esp" type="button" @click="paso = 1">
        <svg style="width: 1rem; height: 0.875rem" viewBox="0 0 18 15" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0.292889 6.65691C-0.0976353 7.04743 -0.0976353 7.6806 0.292889 8.07112L6.65685 14.4351C7.04737 14.8256 7.68054 14.8256 8.07106 14.4351C8.46159 14.0446 8.46159 13.4114 8.07106 13.0209L2.41421 7.36401L8.07106 1.70716C8.46159 1.31664 8.46159 0.68347 8.07106 0.292946C7.68054 -0.0975785 7.04737 -0.0975785 6.65685 0.292946L0.292889 6.65691ZM17.1245 7.36401V6.36401L0.999996 6.36401V7.36401V8.36401L17.1245 8.36401V7.36401Z" fill="black" />
        </svg>
        Volver atrás
      </button>

      <div class="titulo-esp">Selecciona tu especialidad</div>
      <div class="subtitulo-esp">
        Elige la especialidad que mejor se adapte a tu perfil profesional.
      </div>

      <div class="buscador-esp">
        <svg style="width: 1.25rem; height: 1.25rem" class="icono-buscador" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input v-model="busquedaEspecialidad" type="text" placeholder="Buscar especialidad..." />
      </div>

      <p v-if="cargandoEspecialidades" class="text-zinc-400 text-center">
        Cargando especialidades...
      </p>
      <p v-else-if="errorEspecialidades" class="error">{{ errorEspecialidades }}</p>

      <div v-else class="grid-especialidades">
        <button v-for="e in especialidadesFiltradas" :key="e.id_especialidad" type="button" class="especialidad-boton" :class="{ seleccionada: especialidadesSeleccionadas.includes(e.id_especialidad) }" :disabled=" !especialidadesSeleccionadas.includes(e.id_especialidad) && especialidadesSeleccionadas.length >= MAX_ESPECIALIDADES " @click="toggleEspecialidad(e.id_especialidad)">
          {{ e.nombre_especialidad }}
        </button>
      </div>

      <p class="nota-max-esp">
        Podés elegir hasta {{ MAX_ESPECIALIDADES }} especialidades ({{
          especialidadesSeleccionadas.length
        }}/{{ MAX_ESPECIALIDADES }})
      </p>

      <button class="submit-esp" type="button" :disabled="cargando || !especialidadesSeleccionadas.length" @click="confirmarEspecialidades">
        {{ cargando ? 'Guardando...' : 'Continuar' }}
      </button>
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
  background-color: #ffffff;
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
  background: #f1f4f7;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  transition: background-color 0.2s ease;
}

.boton-atras:hover {
  background-color: #e4eaf0;
}

.titulo {
  color: #0f172a;
  font-family: 'Inter', sans-serif;
  font-size: 2.25rem;
  font-weight: 700;
  line-height: normal;
  margin-bottom: 0.375rem;
}

.subtitulo {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.etiqueta-tipo {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.tipo-usuario {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.tipo-boton {
  flex: 1;
  font-family: 'Inter', sans-serif;
  background-color: #ffffff;
  border: 0.0625rem solid #d1d5db;
  padding: 0.875rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 0.75rem;
  color: #111827;
  text-align: left;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.tipo-boton.activo {
  background-color: #eaf4ff;
  border-color: #4a90e2;
  color: #3d6fc2;
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
  color: #9ca3af;
  pointer-events: none;
}

input {
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  border-radius: 0.875rem;
  border: 0.0625rem solid #d1d5db;
  background-color: #f9fafb;
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
  margin-top: 0.5rem;
  background: linear-gradient(90deg, #6aa6f2 0%, #3d6fc2 100%);
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
  color: #dc2626;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.login-link {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.95rem;
  color: #6b7280;
}

.login-link a {
  color: #111827;
  font-weight: 600;
}

.contenedor-especialidad {
  position: relative;
  width: 47.5rem;
  max-width: 92vw;
  margin: 2rem auto;
  padding: 2.1875rem 3.5rem 3.5rem;
  border-radius: 1.5rem;
  background-color: #ffffff;
  box-shadow:
    0 1.5rem 3.75rem -1rem rgba(0, 0, 0, 0.07),
    0 0 5.66875rem 0.375rem rgba(0, 0, 0, 0.4);
}

.boton-atras-esp {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1.0625rem;
  background-color: #f8fafc;
  outline: 0.0625rem solid #e5e7eb;
  outline-offset: -0.0625rem;
  border: none;
  border-radius: 0.75rem;
  color: #111827;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.boton-atras-esp:hover {
  background-color: #eef2f6;
}

.titulo-esp {
  color: #000000;
  font-family: 'Inter', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: normal;
  margin-bottom: 0.375rem;
}

.subtitulo-esp {
  color: #6b7280;
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  font-weight: 400;
  line-height: 1.375rem;
  margin-bottom: 2rem;
}

.buscador-esp {
  position: relative;
  display: flex;
  align-items: center;
  height: 4rem;
  padding: 0 1rem;
  margin-bottom: 2.875rem;
  background-color: #f8fafc;
  outline: 0.0625rem solid #a3a3a3;
  outline-offset: -0.0625rem;
  border-radius: 1rem;
  gap: 0.75rem;
}

.icono-buscador {
  color: #000000;
  flex-shrink: 0;
}

.buscador-esp input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0;
  color: #000000;
  font-size: 0.9rem;
}

.buscador-esp input:focus {
  outline: none;
}

.buscador-esp input::placeholder {
  color: #52525b;
}

.grid-especialidades {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.especialidad-boton {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0.875rem;
  border-radius: 0.875rem;
  background-color: #dbeafe;
  outline: 0.0625rem solid #0ea5e9;
  outline-offset: -0.0625rem;
  border: none;
  color: #000000;
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.3;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.especialidad-boton:hover:not(:disabled):not(.seleccionada) {
  background-color: #bfdbfe;
}

.especialidad-boton.seleccionada {
  background-color: #0ea5e9;
  color: #ffffff;
}

.especialidad-boton:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nota-max-esp {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.submit-esp {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(90deg, #0ea5e9 0%, #3d6fc2 100%);
  color: #ffffff;
  border: none;
  border-radius: 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
}

.submit-esp:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
