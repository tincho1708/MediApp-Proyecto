import { ref } from 'vue'

export type TurnoMedico = {
  id_turno: number
  fecha_hora: string
  notas: string | null
  creado_en: string
  id_pacientes: number
  id_medicos: number
  estado: { id: number; estado: string }
  paciente: { id: number; nombre: string; apellido: string }
  medico: { id: number; nombre: string; apellido: string; especialidades: { id_especialidad: number; nombre_especialidad: string }[] }
}

const turnos = ref<TurnoMedico[]>([])
const cargado = ref(false)
const cargando = ref(false)
const error = ref('')

function token() {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  return sesion.token as string | undefined
}

async function cargarTurnosMedico(forzar = false) {
  if (cargado.value && !forzar) return
  cargando.value = true
  error.value = ''
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/mis-turnos`, {
      headers: { Authorization: `Bearer ${token()}` },
    })
    if (!res.ok) throw new Error()
    turnos.value = await res.json()
    cargado.value = true
  } catch {
    error.value = 'No se pudieron cargar los turnos. Intentá de nuevo más tarde.'
  } finally {
    cargando.value = false
  }
}

async function actualizarEstadoTurno(id: number, accion: 'aceptar' | 'rechazar' | 'cancelar') {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/turnos/${id}/${accion}`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${token()}` },
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'No se pudo actualizar el turno.')

  const i = turnos.value.findIndex(t => t.id_turno === id)
  if (i !== -1) turnos.value[i] = data
  else turnos.value.push(data)

  return data as TurnoMedico
}

export function useTurnosMedico() {
  return { turnos, cargado, cargando, error, cargarTurnosMedico, actualizarEstadoTurno }
}
