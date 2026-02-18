export function normalizeForSearch(str) {
  return str.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

export function stripEmoji(str) {
  return str.replace(/^[\p{Emoji_Presentation}\p{Extended_Pictographic}\s]+/u, '')
}

export function nameCompare(a, b) {
  return stripEmoji(a).localeCompare(stripEmoji(b), undefined, { sensitivity: 'base' })
}
