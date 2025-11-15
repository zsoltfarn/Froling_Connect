import { promises as fs } from 'fs'
import path from 'path'

export type Snapshot = {
  timestamp: string
  pages: Record<string, Record<string, string>>
}

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

export async function readData(): Promise<Snapshot[]> {
  const p = path.join(process.cwd(), '..', 'data.json')
  const buf = await fs.readFile(p, 'utf-8')
  const data = JSON.parse(buf)
  return Array.isArray(data) ? data : [data]
}

export type SeriesPoint = { t: Date; v: number }

export function toSeries(snapshots: Snapshot[], component: string, key: string): SeriesPoint[] {
  const points: SeriesPoint[] = []
  for (const s of snapshots) {
    const pages = s.pages || {}
    const comp = pages[component]
    if (!comp) continue
    const raw = comp[key]
    const num = parseNumber(raw)
    if (num == null) continue
    points.push({ t: new Date(s.timestamp), v: num })
  }
  return points.sort((a, b) => a.t.getTime() - b.t.getTime())
}

export type Bucket = 'hour' | 'day'

export function bucketSeries(points: SeriesPoint[], bucket: Bucket): SeriesPoint[] {
  const map = new Map<number, number[]>()
  for (const p of points) {
    const d = new Date(p.t)
    if (bucket === 'day') {
      d.setHours(0, 0, 0, 0)
    } else {
      d.setMinutes(0, 0, 0)
    }
    const ts = d.getTime()
    const arr = map.get(ts) || []
    arr.push(p.v)
    map.set(ts, arr)
  }
  const out: SeriesPoint[] = []
  for (const [ts, values] of map.entries()) {
    const avg = values.reduce((a, b) => a + b, 0) / values.length
    out.push({ t: new Date(ts), v: avg })
  }
  return out.sort((a, b) => a.t.getTime() - b.t.getTime())
}

export function listNumericKeys(snapshots: Snapshot[], component: string): string[] {
  const set = new Set<string>()
  for (const s of snapshots) {
    const comp = s.pages?.[component]
    if (!comp) continue
    for (const [k, v] of Object.entries(comp)) {
      const num = parseNumber(v)
      if (num != null) set.add(k)
    }
  }
  return Array.from(set).sort()
}