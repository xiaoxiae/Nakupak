import api from '../api'

describe('API interceptors', () => {
  it('adds Authorization header when token exists', () => {
    localStorage.setItem('token', 'test-jwt-token')
    const config = { headers: {} }
    const result = api.interceptors.request.handlers[0].fulfilled(config)
    expect(result.headers.Authorization).toBe('Bearer test-jwt-token')
  })

  it('does not add Authorization header when no token', () => {
    localStorage.removeItem('token')
    const config = { headers: {} }
    const result = api.interceptors.request.handlers[0].fulfilled(config)
    expect(result.headers.Authorization).toBeUndefined()
  })

  it('redirects to /login on 401 response', async () => {
    localStorage.setItem('token', 'some-token')
    const error = { response: { status: 401 } }
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch {
      // expected rejection
    }
    expect(localStorage.getItem('token')).toBeNull()
    expect(window.location.href).toBe('/login')
  })

  it('passes through non-401 errors', async () => {
    const error = { response: { status: 500 } }
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch (e) {
      expect(e.response.status).toBe(500)
    }
  })
})
