import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { vi } from 'vitest'

// Mock the API module
vi.mock('../../services/api', () => ({
  auth: {
    create: vi.fn(),
    join: vi.fn(),
    me: vi.fn(),
  },
}))

import { auth as authApi } from '../../services/api'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('has null initial state', () => {
    const store = useAuthStore()
    expect(store.household).toBeNull()
    expect(store.token).toBeNull()
  })

  it('computes isLoggedIn correctly', () => {
    const store = useAuthStore()
    expect(store.isLoggedIn).toBe(false)
    store.token = 'some-token'
    expect(store.isLoggedIn).toBe(true)
  })

  it('createHousehold sets token and fetches household', async () => {
    authApi.create.mockResolvedValue({ data: { access_token: 'jwt-123' } })
    authApi.me.mockResolvedValue({ data: { token: 'AAAA-BBBB', created_at: '2024-01-01' } })

    const store = useAuthStore()
    await store.createHousehold()
    expect(store.token).toBe('jwt-123')
    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'jwt-123')
    expect(store.household).toEqual({ token: 'AAAA-BBBB', created_at: '2024-01-01' })
  })

  it('joinHousehold sets token and fetches household', async () => {
    authApi.join.mockResolvedValue({ data: { access_token: 'jwt-456' } })
    authApi.me.mockResolvedValue({ data: { token: 'CCCC-DDDD', created_at: '2024-01-01' } })

    const store = useAuthStore()
    await store.joinHousehold('CCCC-DDDD')
    expect(store.token).toBe('jwt-456')
    expect(authApi.join).toHaveBeenCalledWith('CCCC-DDDD')
  })

  it('fetchHousehold sets household data', async () => {
    authApi.me.mockResolvedValue({ data: { token: 'AAAA-BBBB' } })
    const store = useAuthStore()
    store.token = 'jwt-123'
    await store.fetchHousehold()
    expect(store.household).toEqual({ token: 'AAAA-BBBB' })
  })

  it('fetchHousehold calls logout on error', async () => {
    authApi.me.mockRejectedValue(new Error('fail'))
    const store = useAuthStore()
    store.token = 'jwt-bad'
    await store.fetchHousehold()
    expect(store.token).toBeNull()
    expect(store.household).toBeNull()
  })

  it('fetchHousehold skips if no token', async () => {
    const store = useAuthStore()
    await store.fetchHousehold()
    expect(authApi.me).not.toHaveBeenCalled()
  })

  it('logout clears all state', () => {
    const store = useAuthStore()
    store.token = 'jwt-123'
    store.household = { token: 'AAAA-BBBB' }
    store.logout()
    expect(store.token).toBeNull()
    expect(store.household).toBeNull()
    expect(localStorage.removeItem).toHaveBeenCalledWith('token')
  })
})
