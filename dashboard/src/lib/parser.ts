export function parseNumber(raw: unknown): number | null {
  let s = String(raw ?? '').trim()
  if (!s) return null
  s = s.replace(/[^0-9.,\-]/g, '')
  if (!s) return null
  const lastDot = s.lastIndexOf('.')
  const lastComma = s.lastIndexOf(',')
  if (lastComma !== -1 && lastDot === -1) {
    s = s.replace(/,/g, '.')
  } else if (lastDot !== -1 && lastComma !== -1) {
    if (lastComma > lastDot) {
      s = s.replace(/\./g, '')
      s = s.replace(/,/g, '.')
    } else {
      s = s.replace(/,/g, '')
    }
  } else {
    s = s.replace(/,/g, '')
  }
  const n = parseFloat(s)
  return Number.isFinite(n) ? n : null
}