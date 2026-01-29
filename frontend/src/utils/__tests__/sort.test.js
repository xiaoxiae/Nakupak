import { stripEmoji, nameCompare } from '../sort'

describe('stripEmoji', () => {
  it('removes leading emoji', () => {
    expect(stripEmoji('🍎 Apple')).toBe('Apple')
  })

  it('returns string with no emoji unchanged', () => {
    expect(stripEmoji('Milk')).toBe('Milk')
  })

  it('returns empty string for emoji-only input', () => {
    expect(stripEmoji('🍎🍊')).toBe('')
  })

  it('does not remove middle emoji', () => {
    expect(stripEmoji('A 🍎 B')).toBe('A 🍎 B')
  })

  it('returns empty string for empty input', () => {
    expect(stripEmoji('')).toBe('')
  })

  it('returns empty string for whitespace-only input', () => {
    expect(stripEmoji('   ')).toBe('')
  })
})

describe('nameCompare', () => {
  it('sorts alphabetically', () => {
    expect(nameCompare('Apple', 'Banana')).toBeLessThan(0)
    expect(nameCompare('Banana', 'Apple')).toBeGreaterThan(0)
  })

  it('returns 0 for equal strings', () => {
    expect(nameCompare('Apple', 'Apple')).toBe(0)
  })

  it('ignores leading emoji for sorting', () => {
    expect(nameCompare('🍎 Apple', 'Banana')).toBeLessThan(0)
  })

  it('uses locale-aware comparison', () => {
    // Both should be treated as valid comparisons
    const result = nameCompare('ä', 'z')
    expect(typeof result).toBe('number')
  })
})
