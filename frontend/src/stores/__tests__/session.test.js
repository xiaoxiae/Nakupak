import { setActivePinia, createPinia } from 'pinia'
import { useSessionStore } from '../session'
import { vi } from 'vitest'

vi.mock('../../services/api', () => ({
  sessions: {
    start: vi.fn(),
    getActive: vi.fn(),
    toggleCheck: vi.fn(),
    complete: vi.fn(),
    abort: vi.fn(),
    list: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../../services/offline', () => ({
  queueAction: vi.fn(),
}))

import { sessions } from '../../services/api'
import { queueAction } from '../../services/offline'

describe('session store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('isActive is false when no session', () => {
    const store = useSessionStore()
    expect(store.isActive).toBe(false)
  })

  it('isActive is true when session exists', () => {
    const store = useSessionStore()
    store.activeSession = { id: 1, session_items: [] }
    expect(store.isActive).toBe(true)
  })

  it('sortedItems returns empty for no session', () => {
    const store = useSessionStore()
    expect(store.sortedItems).toEqual([])
  })

  it('checkedCount counts checked items', () => {
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [
        { id: 1, checked: true, item: {} },
        { id: 2, checked: false, item: {} },
        { id: 3, checked: true, item: {} },
      ],
    }
    expect(store.checkedCount).toBe(2)
  })

  it('totalCount returns total items', () => {
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [{ id: 1 }, { id: 2 }, { id: 3 }],
    }
    expect(store.totalCount).toBe(3)
  })

  it('toggleCheck optimistically toggles on', async () => {
    sessions.toggleCheck.mockResolvedValue({ data: { checked: true, checked_at: '2024-01-01' } })
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [{ id: 10, checked: false, checked_at: null, item: {} }],
    }
    await store.toggleCheck(10)
    expect(store.activeSession.session_items[0].checked).toBe(true)
  })

  it('toggleCheck optimistically toggles off', async () => {
    sessions.toggleCheck.mockResolvedValue({ data: { checked: false, checked_at: null } })
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [{ id: 10, checked: true, checked_at: '2024-01-01', item: {} }],
    }
    await store.toggleCheck(10)
    expect(store.activeSession.session_items[0].checked).toBe(false)
  })

  it('toggleCheck updates with API response', async () => {
    sessions.toggleCheck.mockResolvedValue({ data: { checked: true, checked_at: '2024-06-15T12:00:00' } })
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [{ id: 10, checked: false, checked_at: null, item: {} }],
    }
    await store.toggleCheck(10)
    expect(store.activeSession.session_items[0].checked_at).toBe('2024-06-15T12:00:00')
  })

  it('toggleCheck queues action on error', async () => {
    sessions.toggleCheck.mockRejectedValue(new Error('Network error'))
    const store = useSessionStore()
    store.activeSession = {
      id: 1,
      session_items: [{ id: 10, checked: false, checked_at: null, item: {} }],
    }
    await store.toggleCheck(10)
    expect(queueAction).toHaveBeenCalledWith({ type: 'toggle_check', itemId: 10 })
  })
})
