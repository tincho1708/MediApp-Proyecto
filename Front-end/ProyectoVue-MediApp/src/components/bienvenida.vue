<script setup lang="ts">
const emit = defineEmits(['ir-a-registro', 'ir-a-login', 'ir-a-medico-paciente'])
</script>

<template>
  <div>
    <nav class="navbar">
      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>
      <div class="navbar-acciones">
        <button class="boton1" @click="emit('ir-a-medico-paciente')">
          <span>Registrar</span>
        </button>
        <button class="boton2" @click="emit('ir-a-login')">
          <span>Iniciar sesión</span>
        </button>
      </div>
    </nav>
    <div class="texto">Tu salud, mas simple.</div>
    <button class="boton3" @click="emit('ir-a-medico-paciente')">
      <span>Descubrela</span>
    </button>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Inter:wght@400;700&display=swap');

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #D9D9D9;
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

.boton1 {
  display: flex;
  gap: 12px;
  font-family: 'Lexend', sans-serif;
  font-size: 28px;
  font-weight: 700;
  background-color: #585858;
  align-items: center;

}
.boton1 span {
  display: flex;
  gap: 12px;
  font-family: 'Lexend', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #000000;
  display: flex;
  margin: 5px; 
  }

  .boton2  {
  display: flex;
  gap: 12px;
  font-family: 'Lexend', sans-serif;
  font-size: 28px;
  font-weight: 700;
  background-color: #585858;
  align-items: center;

}
.boton2 span {
  display: flex;
  gap: 12px;
  font-family: 'Lexend', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #000000;
  display: flex;
  margin: 5px; 
  }

  .boton3 {
  display: flex;
  gap: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 700;
  background-color: #D9D9D9;
  align-items: center;
  position: absolute;
  top: 430px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 28px;
  border-color:#D9D9D9;
}
.boton3 span {
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 700;
  margin: 15px;
  }
  
  .texto {
    font-family: 'Lexend', sans-serif;
    font-size: 60px;
    font-weight: 700;
    color: #000000;
    display: flex;
    justify-content: center;
    margin-top: 300px; 
  }
</style>
