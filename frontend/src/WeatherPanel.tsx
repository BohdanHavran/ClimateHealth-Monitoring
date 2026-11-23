import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { getWeather } from './monitoring-api'
import type { Place, Weather } from './monitoring-api'
import { PlaceSearch } from './PlaceSearch'

export const localTime = (value: string) => new Intl.DateTimeFormat('uk-UA', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
export function WeatherDetails({ weather }: { weather: Weather }) {
  return <div className="weather-details"><div className="metric-grid"><div><span>Температура</span><strong>{weather.avg_temp.toFixed(1)} <small>°C</small></strong></div><div><span>Вологість</span><strong>{weather.humidity.toFixed(0)} <small>%</small></strong></div><div><span>Короткохвильова радіація</span><strong>{weather.solar.toFixed(0)} <small>W/m²</small></strong></div></div>
    <p className="data-caption">Час показників: {localTime(weather.data_time)} · Отримано: {localTime(weather.fetched_at)} · {weather.cached ? 'Із кешу (TTL 5 хв)' : 'Новий запит'}</p>
    <p className="data-caption"><a href="https://open-meteo.com/" target="_blank" rel="noreferrer">Weather data by Open-Meteo.com</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a></p>
    <p className="quality-note">Поточні модельні умови, не вимірювання станції. Радіація — модельне середнє за попередній інтервал, не інструментальне вимірювання. Дані не є медичним прогнозом.</p>
    {weather.quality_issues.includes('data_time:stale') && <p className="inline-error">Час показників застарілий. Перевірте актуальність перед аналізом.</p>}</div>
}

export function WeatherPanel({ onWeather, selectedPlace }: { onWeather?: (weather: Weather) => void; selectedPlace?: Place | null }) {
  const [place, setPlace] = useState<(Pick<Place, 'name' | 'lat' | 'lon'> & { id?: number }) | null>(null)
  const [coordinates, setCoordinates] = useState({ lat: '', lon: '' })
  const [weather, setWeather] = useState<Weather | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const controller = useRef<AbortController | null>(null)
  const currentPlace = selectedPlace ?? place
  useEffect(() => { controller.current?.abort(); setWeather(null); setError(''); setLoading(false) }, [currentPlace?.id, currentPlace?.lat, currentPlace?.lon])
  useEffect(() => () => controller.current?.abort(), [])
  function useCoordinates(event: FormEvent) {
    event.preventDefault()
    const lat = Number(coordinates.lat), lon = Number(coordinates.lon)
    if (!coordinates.lat.trim() || !coordinates.lon.trim() || !Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) { setError('Перевірте широту та довготу.'); return }
    setPlace({ name: 'Введені координати', lat, lon })
  }
  async function load() {
    if (!currentPlace) return
    controller.current?.abort()
    const active = new AbortController(); controller.current = active
    setLoading(true); setError(''); setWeather(null)
    try { const value = await getWeather(currentPlace, active.signal); if (!active.signal.aborted) { setWeather(value); onWeather?.(value) } }
    catch (e) { if (!active.signal.aborted) setError(e instanceof Error ? e.message : 'Погода недоступна.') }
    finally { if (!active.signal.aborted) setLoading(false) }
  }
  return <section className="panel weather-panel"><div className="panel-heading"><div><p className="eyebrow">ПОТОЧНІ УМОВИ</p><h2>Поточна погода за координатами</h2><p>Виберіть населений пункт або введіть координати. Історичні записи до місця не прив’язуються.</p></div></div><div className="panel-body">
    {!selectedPlace && <PlaceSearch onSelect={setPlace} />}
    {!selectedPlace && <details><summary>Погода за введеними координатами</summary><form className="filter-bar coordinates-form" onSubmit={useCoordinates} noValidate><label htmlFor="weather-lat">Широта, °<input id="weather-lat" type="number" step="any" min="-90" max="90" value={coordinates.lat} onChange={e => setCoordinates(v => ({ ...v, lat: e.target.value }))} /></label><label htmlFor="weather-lon">Довгота, °<input id="weather-lon" type="number" step="any" min="-180" max="180" value={coordinates.lon} onChange={e => setCoordinates(v => ({ ...v, lon: e.target.value }))} /></label><button>Використати координати</button></form><p className="data-caption">Координати введені користувачем; назва населеного пункту для них не припускається.</p></details>}
    {currentPlace ? <div className="selected-place"><span><strong>{currentPlace.name}</strong><small>{currentPlace.lat.toFixed(4)}, {currentPlace.lon.toFixed(4)}</small></span><button onClick={load} disabled={loading}>{loading ? 'Отримання…' : 'Отримати погоду'}</button></div> : <p className="empty-hint">Виберіть населений пункт. Погодних значень до запиту немає.</p>}
    {loading && <p role="status">Очікуємо відповідь погодного провайдера…</p>}
    {error && <p role="alert" className="inline-error">{error}</p>}
    {weather && <WeatherDetails weather={weather} />}
  </div></section>
}
