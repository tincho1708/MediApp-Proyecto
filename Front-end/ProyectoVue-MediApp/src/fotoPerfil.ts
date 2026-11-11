export function actualizarSesion(cambios: Record<string, string | null>) {
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  localStorage.setItem('sesion', JSON.stringify({ ...sesion, ...cambios }))
}

export async function subirFoto(evento: Event) {
  const input = evento.target as HTMLInputElement
  const archivo = input.files?.[0]
  input.value = ''
  if (!archivo) return null

  const datos = new FormData()
  datos.append('archivo', archivo)
  const sesion = JSON.parse(localStorage.getItem('sesion') || '{}')
  const res = await fetch(`${import.meta.env.VITE_API_URL}/fotos/mia`, {
    method: 'PUT',
    headers: { Authorization: `Bearer ${sesion.token}` },
    body: datos,
  }).catch(() => null)
  const respuesta = await res?.json().catch(() => null)
  if (!res?.ok) throw new Error(typeof respuesta?.detail === 'string' ? respuesta.detail : 'No se pudo subir la foto.')

  actualizarSesion({ foto: respuesta.foto })
  return respuesta.foto as string
}
