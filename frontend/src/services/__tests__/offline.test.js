import { initDB, queueAction, getQueuedActions, removeFromQueue, clearQueue } from '../offline'

describe('offline queue', () => {
  beforeEach(async () => {
    // Re-initialize DB for a clean state
    await initDB()
    await clearQueue()
  })

  it('initializes IndexedDB', async () => {
    const db = await initDB()
    expect(db).toBeDefined()
    expect(db.objectStoreNames.contains('syncQueue')).toBe(true)
  })

  it('queues an action', async () => {
    await queueAction({ type: 'toggle_check', itemId: 1 })
    const actions = await getQueuedActions()
    expect(actions).toHaveLength(1)
    expect(actions[0].type).toBe('toggle_check')
    expect(actions[0].itemId).toBe(1)
  })

  it('adds timestamp to queued actions', async () => {
    await queueAction({ type: 'test' })
    const actions = await getQueuedActions()
    expect(actions[0].timestamp).toBeDefined()
    expect(typeof actions[0].timestamp).toBe('number')
  })

  it('gets all queued actions', async () => {
    await queueAction({ type: 'a' })
    await queueAction({ type: 'b' })
    const actions = await getQueuedActions()
    expect(actions).toHaveLength(2)
  })

  it('removes a specific action from queue', async () => {
    const id = await queueAction({ type: 'a' })
    await queueAction({ type: 'b' })
    await removeFromQueue(id)
    const actions = await getQueuedActions()
    expect(actions).toHaveLength(1)
    expect(actions[0].type).toBe('b')
  })

  it('clears the queue', async () => {
    await queueAction({ type: 'a' })
    await queueAction({ type: 'b' })
    await clearQueue()
    const actions = await getQueuedActions()
    expect(actions).toHaveLength(0)
  })

  it('auto-initializes on first call', async () => {
    // clearQueue already tested auto-init; test queueAction directly
    const actions = await getQueuedActions()
    expect(Array.isArray(actions)).toBe(true)
  })
})
