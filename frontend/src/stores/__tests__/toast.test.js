import { setActivePinia, createPinia } from 'pinia'
import { useToastStore } from '../toast'

describe('toast store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows a toast with message', () => {
    const store = useToastStore()
    store.show('Hello')
    expect(store.toasts).toHaveLength(1)
    expect(store.toasts[0].message).toBe('Hello')
  })

  it('replaces previous toast', () => {
    const store = useToastStore()
    store.show('First')
    store.show('Second')
    expect(store.toasts).toHaveLength(1)
    expect(store.toasts[0].message).toBe('Second')
  })

  it('assigns unique ids', () => {
    const store = useToastStore()
    store.show('A')
    const id1 = store.toasts[0].id
    store.show('B')
    const id2 = store.toasts[0].id
    expect(id1).not.toBe(id2)
  })

  it('auto-dismisses after default duration', () => {
    const store = useToastStore()
    store.show('Bye')
    expect(store.toasts).toHaveLength(1)
    vi.advanceTimersByTime(3000)
    expect(store.toasts).toHaveLength(0)
  })

  it('supports custom duration', () => {
    const store = useToastStore()
    store.show('Custom', { duration: 1000 })
    vi.advanceTimersByTime(999)
    expect(store.toasts).toHaveLength(1)
    vi.advanceTimersByTime(2)
    expect(store.toasts).toHaveLength(0)
  })
})
