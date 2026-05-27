<script setup lang="ts">
const emit = defineEmits(['ir-a-bienvenida'])
</script>

<template>
    <div class="navbar">

      <div class="navbar-logo">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
        <span>App</span>
      </div>    
      <div class="navbar-acciones">
        <button class="campoo">MediBot</button>
        <button class="campoo">Mis pacientes</button>
        <button class="campoo">Notificaciones</button>
        <button class="campoo">MediApp+</button>
        <button class="barra">
          <div>──────</div>
          <div>──────</div>
          <div>──────</div>
        </button>
      </div>

    </div>
</template>

<style>
.navbar {
  height: 115px;
}
.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-logo img {
  width: 125px;
  height: 125px;
}

.navbar-logo span {
  font-family: 'Lexend', sans-serif;
  font-size: 47px;
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
  flex-direction: row;
  gap: 50px;
}
.campoo {
  text-align: center;
  width: 206px;
  height: 73px;
  background: #2185DA;
  border-radius: 40px;
  color: #000;
  font-family: Inter;
  font-size: 20px;
  font-weight: 200;
  line-height: normal;
  border: none;
  cursor: pointer;  
  font-family: 'Lexend', 'sans-serif';
}

.barra {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-right: 20px;
}
</style>