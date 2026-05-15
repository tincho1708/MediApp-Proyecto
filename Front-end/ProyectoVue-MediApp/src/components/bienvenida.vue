<template>
  <nav class="navbar">

    <div class="navbar-logo">
      <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" />
      <span>App</span>
    </div>

    <div class="navbar-acciones">
      <slot />
    </div>

  </nav>
</template>

<style scoped>

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
  width: 80px;
  height: 80px;
}

.navbar-logo span {
  font-size: 28px;
  font-weight: bold;
  background: linear-gradient(90deg, #204BAC 0%, #1F6BC6 36%, #1F85DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: -14px;
  margin-top: 14px;
  
}

.navbar-acciones {
  display: flex;
  gap: 12px;
}
</style>
