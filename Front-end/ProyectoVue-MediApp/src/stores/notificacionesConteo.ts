import { ref, onMounted, onUnmounted } from 'vue'

const conteoNoLeidas = ref(0)

function token() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  return sesion.token as string | undefined
}

async function cargarConteoNoLeidas(silencioso = false) {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/notificaciones/no-leidas`, {
      headers: { Authorization: `Bearer ${token()}` },
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    conteoNoLeidas.value = data.count
  } catch {
    if (!silencioso) conteoNoLeidas.value = 0
  }
}

function usarPollingConteoNoLeidas(intervaloMs = 6000) {
  let intervalId: ReturnType<typeof setInterval> | undefined

  onMounted(() => {
    cargarConteoNoLeidas()
    intervalId = setInterval(() => cargarConteoNoLeidas(true), intervaloMs)
  })

  onUnmounted(() => {
    if (intervalId !== undefined) clearInterval(intervalId)
  })
}

function resetConteoNoLeidas() {
  conteoNoLeidas.value = 0
}

export function useConteoNoLeidas() {
  return { conteoNoLeidas, cargarConteoNoLeidas, usarPollingConteoNoLeidas, resetConteoNoLeidas }
}
