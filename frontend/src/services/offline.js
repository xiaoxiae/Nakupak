const DB_NAME = 'nakupak-offline'
const DB_VERSION = 1
const QUEUE_STORE = 'syncQueue'

let db = null

export async function initDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      db = request.result
      resolve(db)
    }

    request.onupgradeneeded = (event) => {
      const database = event.target.result
      if (!database.objectStoreNames.contains(QUEUE_STORE)) {
        database.createObjectStore(QUEUE_STORE, { keyPath: 'id', autoIncrement: true })
      }
    }
  })
}

export async function queueAction(action) {
  if (!db) await initDB()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([QUEUE_STORE], 'readwrite')
    const store = transaction.objectStore(QUEUE_STORE)
    const request = store.add({ ...action, timestamp: Date.now() })

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

export async function getQueuedActions() {
  if (!db) await initDB()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([QUEUE_STORE], 'readonly')
    const store = transaction.objectStore(QUEUE_STORE)
    const request = store.getAll()

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

export async function clearQueue() {
  if (!db) await initDB()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([QUEUE_STORE], 'readwrite')
    const store = transaction.objectStore(QUEUE_STORE)
    const request = store.clear()

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

export async function removeFromQueue(id) {
  if (!db) await initDB()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([QUEUE_STORE], 'readwrite')
    const store = transaction.objectStore(QUEUE_STORE)
    const request = store.delete(id)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}
