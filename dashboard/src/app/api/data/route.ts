import { NextResponse } from 'next/server'
import { readData } from '@/lib/data'

export async function GET() {
  try {
    const snapshots = await readData()
    const components = Array.from(
      new Set(
        snapshots.flatMap((s) => Object.keys(s.pages || {}))
      )
    ).sort()
    return NextResponse.json({ snapshots, components })
  } catch (e: any) {
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}