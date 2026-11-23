export type Observation = {
  id: number; year: number | null; month: number | null; avg_temp: number | null;
  solar_irradiance: number | null; humidity: number | null; quality_issues: string[];
}
export type ObservationPage = { data: Observation[]; meta: { next_after_id: number | null; received_at?: string } }

function nullableNumber(value: unknown): value is number | null {
  return value === null || (typeof value === 'number' && Number.isFinite(value))
}
export function isObservation(value: unknown): value is Observation {
  if (typeof value !== 'object' || value === null) return false
  const r = value as Record<string, unknown>
  return typeof r.id === 'number' && Number.isSafeInteger(r.id) && r.id > 0
    && ['year', 'month', 'avg_temp', 'solar_irradiance', 'humidity'].every(k => nullableNumber(r[k]))
    && Array.isArray(r.quality_issues) && r.quality_issues.every(v => typeof v === 'string')
}
export async function getObservations(year: string, afterId: number, signal: AbortSignal): Promise<ObservationPage> {
  const params = new URLSearchParams({ limit: '50', after_id: String(afterId) })
  if (year) params.set('year', year)
  const response = await fetch(`/api/v1/observations?${params}`, { signal,
    headers: { Accept: 'application/json' }, credentials: 'same-origin' })
  if (!response.ok) {
    if (response.status === 429) throw new Error('Забагато запитів. Спробуйте через хвилину.')
    throw new Error('Не вдалося отримати спостереження. Перевірте доступність сервера.')
  }
  const body: unknown = await response.json()
  if (typeof body !== 'object' || body === null) throw new Error('Некоректна відповідь сервера.')
  const page = body as Record<string, unknown>
  if (!Array.isArray(page.data) || !page.data.every(isObservation) || page.data.length > 50
      || typeof page.meta !== 'object' || page.meta === null) throw new Error('Некоректна відповідь сервера.')
  const cursor = (page.meta as Record<string, unknown>).next_after_id
  if (cursor !== null && (typeof cursor !== 'number' || !Number.isSafeInteger(cursor) || cursor <= afterId)) {
    throw new Error('Некоректна пагінація сервера.')
  }
  const receivedAt = (page.meta as Record<string, unknown>).received_at
  return { data: page.data, meta: { next_after_id: cursor as number | null,
    received_at: typeof receivedAt === 'string' && Number.isFinite(Date.parse(receivedAt)) ? receivedAt : undefined } }
}
