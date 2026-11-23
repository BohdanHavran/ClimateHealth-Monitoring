export type Place = { id: number; name: string; lat: number; lon: number; population: number | null }
export type ClimateInputs = { avg_temp: number; solar: number; humidity: number }
export type Weather = ClimateInputs & { lat: number; lon: number; source: string; data_time: string; fetched_at: string; cached: boolean; quality_issues: string[] }
export type HriResult = { hri: number; inputs: ClimateInputs; effective_inputs: ClimateInputs; clipped: boolean; method: string; medical_prediction: false }
type JsonObject = Record<string, unknown>
const object = (v: unknown): v is JsonObject => typeof v === 'object' && v !== null && !Array.isArray(v)
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)
const inputs = (v: unknown): v is ClimateInputs & JsonObject => object(v) && ['avg_temp', 'solar', 'humidity'].every(k => finite(v[k]))

async function request(path: string, init: RequestInit = {}): Promise<JsonObject> {
  const timeout = AbortSignal.timeout(12000)
  const signal = init.signal ? AbortSignal.any([init.signal, timeout]) : timeout
  let response: Response
  try { response = await fetch('/api/v1' + path, { ...init, signal, credentials: 'same-origin', headers: { Accept: 'application/json', ...init.headers } }) }
  catch (error) { if (init.signal?.aborted) throw error; throw new Error('Сервер не відповідає або час очікування вичерпано. Повторіть запит.', { cause: error }) }
  if (!response.ok) {
    if (response.status === 429) throw new Error('Ліміт запитів вичерпано. Спробуйте через хвилину.')
    if (response.status === 503) throw new Error('Джерело даних тимчасово недоступне. Повторіть запит пізніше.')
    throw new Error('Запит не виконано. Перевірте введені параметри.')
  }
  let body: unknown
  try { body = await response.json() } catch { throw new Error('Некоректний формат відповіді API.') }
  if (!object(body)) throw new Error('Некоректний формат відповіді API.')
  return body
}

function places(body: JsonObject, maximum: number): Place[] {
  if (!Array.isArray(body.data) || body.data.length > maximum || !body.data.every(p => object(p)
    && finite(p.id) && Number.isSafeInteger(p.id) && p.id > 0 && typeof p.name === 'string' && p.name.length <= 200
    && finite(p.lat) && p.lat >= -90 && p.lat <= 90 && finite(p.lon) && p.lon >= -180 && p.lon <= 180
    && (p.population === null || (finite(p.population) && p.population >= 0)))) throw new Error('Некоректні географічні дані API.')
  return body.data as Place[]
}
export async function searchPlaces(query: string, signal?: AbortSignal) {
  return places(await request('/places/search?' + new URLSearchParams({ q: query, limit: '10' }), { signal }), 10)
}
export async function getPlaces(bounds: { south: number; north: number; west: number; east: number }, signal?: AbortSignal) {
  const params = new URLSearchParams({ ...Object.fromEntries(Object.entries(bounds).map(([k, v]) => [k, String(v)])), limit: '200' })
  return places(await request('/places?' + params, { signal }), 200)
}
export async function getWeather(place: Pick<Place, 'lat' | 'lon'>, signal?: AbortSignal): Promise<Weather> {
  const { data } = await request('/weather?' + new URLSearchParams({ lat: String(place.lat), lon: String(place.lon) }), { signal })
  if (!inputs(data) || !object(data) || !finite(data.lat) || !finite(data.lon) || data.source !== 'Open-Meteo'
    || typeof data.data_time !== 'string' || !Number.isFinite(Date.parse(data.data_time))
    || typeof data.fetched_at !== 'string' || !Number.isFinite(Date.parse(data.fetched_at))
    || typeof data.cached !== 'boolean' || !Array.isArray(data.quality_issues) || !data.quality_issues.every(s => typeof s === 'string')) {
    throw new Error('Некоректні погодні дані API.')
  }
  return data as Weather
}
export async function calculateHri(values: ClimateInputs, signal?: AbortSignal): Promise<HriResult> {
  const { data } = await request('/hri', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values), signal })
  if (!object(data) || !finite(data.hri) || data.hri < 0 || data.hri > 1 || !inputs(data.inputs) || !inputs(data.effective_inputs)
    || typeof data.clipped !== 'boolean' || data.method !== 'fuzzy_rules_27' || data.medical_prediction !== false) {
    throw new Error('Некоректний результат HRI API.')
  }
  return data as HriResult
}
