<script setup lang="ts">
const emit = defineEmits(['ir-a-registro', 'ir-a-login'])
</script>

<template>
  <div>
    <nav class="navbar">
      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
      <div class="navbar-acciones">
        <button class="boton1" @click="emit('ir-a-login')">Iniciar sesión</button>
        <button class="boton2" @click="emit('ir-a-registro')">Registrarse</button>
      </div>
    </nav>

    <div class="contenido">

      <div class="titulo">La mejor herramienta de organizacion para <span class="texto-acento">profesionales</span>.</div>

      <div class="contenedor1">
        <img src="@/assets/imagenes/imagen-bienvenida.png" alt="Imagen de bienvenida" />
      </div>

      <div class="columna-izq">
        <p class="descripcion">Organiza tu agenda, gestiona a tus pacientes y administra tus turnos desde una única plataforma, segura y centralizada.</p>

        <div class="accede-con"><span>Accede con</span></div>

        <div class="fila-social">
          <button class="social-boton" @click="emit('ir-a-login')">
            <img src="@/assets/imagenes/google.png" alt="Google" />
            Continuar con Google
          </button>
          <button class="social-boton" @click="emit('ir-a-login')">
            <img src="@/assets/imagenes/microsoft.png" alt="Microsoft" />
            Continuar con Microsoft
          </button>
        </div>

        <p class="sin-cuenta">¿No tienes cuenta? <a href="#" @click.prevent="emit('ir-a-registro')">Regístrate</a></p>
      </div>

    </div>
  </div>

</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.contenido {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #BFDBFE 0%, #FFFFFF 50%, #BFDBFE 100%);
}

.titulo {
  position: absolute;
  left: 4rem;
  top: 7.9375rem;
  width: 78.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 3.5rem;
  font-weight: 500;
  line-height: 4.9rem;
  color: #000000;
  z-index: 2;
}

.columna-izq {
  position: absolute;
  left: 4rem;
  top: 22.6875rem;
  width: 38.75rem;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 2.75rem;
}

.contenedor1 {
  position: absolute;
  left: 48.85rem;
  top: 15.8125rem;
  width: 36.8rem;
  height: 26rem;
  background-color: #D9D9D9;
  border-radius: 1.25rem;
  overflow: hidden;
  box-shadow: 0 1rem 2.86875rem 1.1875rem rgba(26, 58, 96, 0.19),
              0 0.25rem 1.0375rem 0 rgba(26, 58, 96, 0.06);
  z-index: 1;
}

.contenedor1 img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.texto-acento {
  color: #3D8CE0;
}

.descripcion {
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  font-weight: 400;
  line-height: 2rem;
  color: #3F3F46;
}

.accede-con {
  display: flex;
  align-items: center;
  height: 1.5rem;
  gap: 1rem;
  color: #4B5563;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
}

.accede-con::before,
.accede-con::after {
  content: '';
  flex: 1;
  height: 0.0625rem;
  background-color: #CBD5E1;
}

.fila-social {
  display: flex;
  gap: 1rem;
  height: 4rem;
}

.social-boton {
  flex: 1;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  color: #111827;
  cursor: pointer;
  background-color: #FFFFFF;
  outline: 0.0625rem solid #D4D4D4;
  outline-offset: -0.0625rem;
  border: none;
  border-radius: 1rem;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: background-color 0.2s ease;
}

.social-boton img {
  width: 1.5rem;
  height: 1.5rem;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.social-boton:hover {
  background-color: #F9FAFB;
}

.sin-cuenta {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: #4B5563;
}

.sin-cuenta a {
  color: #0EA5E9;
  font-weight: 500;
  text-decoration: underline;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #FFFFFF;
  box-sizing: border-box;
  padding: 0.5rem 1.5rem;
  z-index: 100;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-logo img {
  width: 5.775rem;
  height: 5.775rem;
}

.navbar-logo span {
  font-family: 'Inter', sans-serif;
  font-size: 2.425rem;
  font-weight: 500;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -0.875rem;
  margin-top: 0.4375rem;
}

.navbar-acciones {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.boton1 {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  background-color: white;
  border: 0.0625rem solid #D1D5DB;
  border-radius: 1.5625rem;
  cursor: pointer;
  padding: 0.625rem 1.5rem;
  color: #000000;
}
.boton2 {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  background-color: #4A90E2;
  border: none;
  border-radius: 1.5625rem;
  cursor: pointer;
  padding: 0.625rem 1.5rem;
  color: #FFFFFF;
}

.boton1:hover, .boton2:hover {
  opacity: 0.85;
}
</style>
