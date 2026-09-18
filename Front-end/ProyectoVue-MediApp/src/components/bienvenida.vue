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
        <button class="boton1" @click="emit('ir-a-login')">Iniciar sesion</button>
        <button class="boton2" @click="emit('ir-a-registro')">Registrarse</button>
      </div>
    </nav>

    <div class="contenido">

      <div class="columna-izq">
        <div class="texto">La mejor herramienta de organizacion para profesionales.</div>

        <div class="texto-sesion1" @click="emit('ir-a-login')">Iniciar sesion con <img src="@/assets/imagenes/google.png" alt="Google" /></div>
        <div class="texto-sesion2" @click="emit('ir-a-login')">Iniciar sesion con <img src="@/assets/imagenes/microsoft.png" alt="Microsoft" /></div>

        <p class="sin-cuenta">¿No tienes cuenta? <a href="#" @click.prevent="emit('ir-a-registro')">Crea una</a></p>
      </div>

      <div class="columna-der">
        <div class="contenedor1">
          <img src="@/assets/imagenes/imagen-bienvenida.png" alt="Imagen de bienvenida" />
        </div>
      </div>

    </div>
  </div>

</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

.contenido {
  min-height: 100vh;
  padding-top: 7.25rem;
  background: linear-gradient(180deg, #EAFAFF 0%, #44A6D4 100%);
  display: flex;
  align-items: center;
  padding-left: 3.75rem;
  padding-right: 3.75rem;
  gap: 3.75rem;
}

.columna-izq {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 3.75rem;
}

.columna-der {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 3.75rem;
}

.texto {
  font-family: 'Inter', sans-serif;
  font-size: 3.125rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 0.625rem;
}

.texto-sesion1, .texto-sesion2 {
  font-family: 'Inter', sans-serif;
  font-size: 1.875rem;
  font-weight: 400;
  color: #000000;
  cursor: pointer;
  border: 0.125rem solid #000000;
  border-radius: 2.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
}


.texto-sesion1 img {
  width: 2.9375rem;
  height: 2.9375rem;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion2 img {
  width: 2.1875rem;
  height: 2.1875rem;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion1:hover, .texto-sesion2:hover {
  background-color: rgba(255,255,255,0.3);
}

.sin-cuenta {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: #000000;
  text-align: center;
}

.sin-cuenta a {
  color: #000000;
  font-weight: 700;
}

.contenedor1 {
  background-color: #D9D9D9;
  width: 100%;
  max-width: 36.86rem;
  border-radius: 1.25rem;
  border: 0.5rem solid #5FA8D8;
  overflow: hidden;
}

.contenedor1 img {
  width: 100%;
  height: auto;
  display: block;
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
  width: 6.25rem;
  height: 6.25rem;
}

.navbar-logo span {
  font-family: 'Inter', sans-serif;
  font-size: 2.6875rem;
  font-weight: 700;
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
  font-size: 1.125rem;
  font-weight: 700;
  background-color: white;
  border: 0.0625rem solid #2E9CE0;
  border-radius: 0.75rem;
  cursor: pointer;
  padding: 0.625rem 1.5rem;
  color: #000000;
}
.boton2 {
  font-family: 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  background-color: #2E9CE0;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  padding: 0.625rem 1.5rem;
  color: #000000;
}

.boton1:hover, .boton2:hover {
  opacity: 0.85;
}
</style>
