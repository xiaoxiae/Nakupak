export function stripEmoji(str) {
  return str.replace(/^[\p{Emoji_Presentation}\p{Extended_Pictographic}\s]+/u, '')
}

export function nameCompare(a, b) {
  return stripEmoji(a).localeCompare(stripEmoji(b), undefined, { sensitivity: 'base' })
}
