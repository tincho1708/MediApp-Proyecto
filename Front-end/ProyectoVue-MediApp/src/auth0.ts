import { createAuth0Client, type Auth0Client } from '@auth0/auth0-spa-js'

let clientPromise: Promise<Auth0Client> | null = null

function getClient() {
  if (!clientPromise) {
    clientPromise = createAuth0Client({
      domain: import.meta.env.VITE_AUTH0_DOMAIN,
      clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
      authorizationParams: {
        redirect_uri: window.location.origin,
      },
      cacheLocation: 'memory',
    })
  }
  return clientPromise
}

export async function obtenerIdTokenGoogle(): Promise<string> {
  const auth0 = await getClient()
  await auth0.loginWithPopup({
    authorizationParams: { connection: 'google-oauth2' },
  })
  const claims = await auth0.getIdTokenClaims()
  const idToken = claims?.__raw
  await auth0.logout({ openUrl: false })
  if (!idToken) throw new Error('No se pudo obtener el token de Google.')
  return idToken
}
