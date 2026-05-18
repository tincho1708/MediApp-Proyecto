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
        <button class="boton1" @click="emit('ir-a-registro')">Registrar</button>
        <button class="boton2" @click="emit('ir-a-login')">Iniciar sesión</button>
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
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.contenido {
  min-height: 100vh;
  padding-top: 116px;
  background: linear-gradient(180deg, #EAFAFF 0%, #44A6D4 100%);
  display: flex;
  align-items: center;
  padding-left: 60px;
  padding-right: 60px;
  gap: 60px;
}

.columna-izq {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.columna-der {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.texto {
  font-family: 'Lexend', sans-serif;
  font-size: 50px;
  font-weight: 700;
  color: #000000;
  margin-bottom: 10px;
}

.texto-sesion1, .texto-sesion2 {
  font-family: 'Inter', sans-serif;
  font-size: 30px;
  font-weight: 400;
  color: #000000;
  cursor: pointer;
  border: 2px solid #000000;
  border-radius: 40px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}


.texto-sesion1 img {
  width: 47px;
  height: 47px;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion2 img {
  width: 35px;
  height: 35px;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.texto-sesion1:hover, .texto-sesion2:hover {
  background-color: rgba(255,255,255,0.3);
}

.sin-cuenta {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
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
  max-width: 560px;
  border-radius: 20px;
  border: 8px solid #ccc;
  overflow: hidden;
}

.contenedor1 img {
  width: 100%;
  height: auto;
  object-fit: contain;
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
  padding: 8px 24px;
  z-index: 100;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-logo img {
  width: 100px;
  height: 100px;
}

.navbar-logo span {
  font-family: 'Lexend', sans-serif;
  font-size: 43px;
  font-weight: 700;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -14px;
  margin-top: 7px;
}

.navbar-acciones {
  display: flex;
  align-items: center;
  gap: 12px;
}

.boton1, .boton2 {
  font-family: 'Lexend', sans-serif;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(90deg, #EAFAFF 0%, #44A6D4 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  padding: 10px 24px;
  color: #000000;
}

.boton1:hover, .boton2:hover {
  opacity: 0.85;
}
</style>
