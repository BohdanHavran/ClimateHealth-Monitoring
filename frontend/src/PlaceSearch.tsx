import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { searchPlaces } from './monitoring-api'
import type { Place } from './monitoring-api'

export function PlaceSearch({ onSelect }: { onSelect: (place: Place) => void }) {
  const [query, setQuery] = useState('')
  const [rows, setRows] = useState<Place[] | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const controller = useRef<AbortController | null>(null)
  useEffect(() => () => controller.current?.abort(), [])
  async function search(event: FormEvent) {
    event.preventDefault()
    controller.current?.abort()
    const active = new AbortController(); controller.current = active
    setLoading(true); setError(''); setRows(null)
    try { const result = await searchPlaces(query.trim(), active.signal); if (!active.signal.aborted) setRows(result) }
    catch (e) { if (!active.signal.aborted) setError(e instanceof Error ? e.message : 'Пошук недоступний.') }
    finally { if (!active.signal.aborted) setLoading(false) }
  }
  return <div className="place-search"><form className="filter-bar" onSubmit={search}><label htmlFor="place-query">Населений пункт<input id="place-query" value={query} minLength={2} maxLength={100} required placeholder="Наприклад, Львів" onChange={e => setQuery(e.target.value)} /></label><button disabled={loading || query.trim().length < 2}>Знайти місто</button></form>
    {loading && <p role="status">Пошук у довіднику MySQL…</p>}
    {error && <p role="alert" className="inline-error">{error}</p>}
    {rows?.length === 0 && <p>Населених пунктів не знайдено. Спробуйте українську або латинську назву.</p>}
    {rows && rows.length > 0 && <ul className="place-results">{rows.map(place => <li key={place.id}><button type="button" className="secondary" onClick={() => { controller.current?.abort(); setRows(null); onSelect(place) }}>{place.name}<small>{place.lat.toFixed(4)}, {place.lon.toFixed(4)} · ID {place.id}</small></button></li>)}</ul>}
  </div>
}
