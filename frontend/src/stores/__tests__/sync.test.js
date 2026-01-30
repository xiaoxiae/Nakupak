import { setActivePinia, createPinia } from 'pinia'
import { vi } from 'vitest'

vi.mock('../../services/api', () => ({
  shoppingList: {
    toggleCheck: vi.fn(),
  },
}))

vi.mock('../../services/offline', () => ({
  getQueuedActions: vi.fn(),
  removeFromQueue: vi.fn(),
}))

import { useSyncStore } from '../sync'
import { useListStore } from '../list'
import { shoppingList } from '../../services/api'
import { getQueuedActions, removeFromQueue } from '../../services/offline'

describe('sync store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct initial state', () => {
    const store = useSyncStore()
    expect(store.ws).toBeNull()
    expect(store.connected).toBe(false)
  })

  it('offline reflects navigator.onLine', () => {
    const store = useSyncStore()
    // jsdom defaults navigator.onLine to true
    expect(typeof store.offline).toBe('boolean')
  })

  it('setupOfflineDetection listens for online/offline events', () => {
    const addSpy = vi.spyOn(window, 'addEventListener')
    const store = useSyncStore()
    store.setupOfflineDetection()
    const eventNames = addSpy.mock.calls.map(c => c[0])
    expect(eventNames).toContain('online')
    expect(eventNames).toContain('offline')
    addSpy.mockRestore()
  })

  it('offline event sets offline to true', () => {
    const store = useSyncStore()
    store.setupOfflineDetection()
    window.dispatchEvent(new Event('offline'))
    expect(store.offline).toBe(true)
  })

  it('online event sets offline to false', () => {
    const store = useSyncStore()
    store.offline = true
    store.setupOfflineDetection()

    // Mock getQueuedActions to prevent errors during replayQueue
    getQueuedActions.mockResolvedValue([])

    window.dispatchEvent(new Event('online'))
    expect(store.offline).toBe(false)
  })

  it('disconnect closes websocket', () => {
    const store = useSyncStore()
    const mockClose = vi.fn()
    store.ws = { close: mockClose }
    store.disconnect()
    expect(mockClose).toHaveBeenCalled()
  })

  it('disconnect is safe when no ws', () => {
    const store = useSyncStore()
    expect(() => store.disconnect()).not.toThrow()
  })
})
