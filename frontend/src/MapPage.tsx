import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { calculateHri, getPlaces } from './monitoring-api'
import type { HriResult, Place, Weather } from './monitoring-api'
import type { Bounds } from './LeafletMap'
import { PlaceSearch } from './PlaceSearch'
import { WeatherPanel } from './WeatherPanel'

const LeafletMap = lazy(() => import('./LeafletMap').then(module => ({ default: module.LeafletMap })))
const initialBounds = { south: 44, north: 53, west: 22, east: 41 }

export function MapPage() {
  const [bounds, setBounds] = useState<Bounds>(initialBounds)
  const [queryBounds, setQueryBounds] = useState<Bounds>(initialBounds)
  const [places, setPlaces] = useState<Place[]>([])
  const [selected, setSelected] = useState<Place | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tileError, setTileError] = useState(false)
  const [weather, setWeather] = useState<Weather | null>(null)
  const [hri, setHri] = useState<HriResult | null>(null)
  const [hriLoading, setHriLoading] = useState(false)
  const [hriError, setHriError] = useState('')
  const hriController = useRef<AbortController | null>(null)
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true); setError(''); setPlaces([])
    getPlaces(queryBounds, controller.signal).then(rows => { if (!controller.signal.aborted) setPlaces(rows) })
      .catch(e => { if (!controller.signal.aborted) setError(e instanceof Error ? e.message : 'Карта недоступна.') })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [queryBounds])
  useEffect(() => () => hriController.current?.abort(), [])
  function choose(place: Place) { hriController.current?.abort(); setSelected(place); setWeather(null); setHri(null); setHriError(''); setHriLoading(false) }
  async function analyze() {
    if (!weather) return
    hriController.current?.abort()
    const active = new AbortController(); hriController.current = active
    setHriLoading(true); setHriError(''); setHri(null)
    try { const result = await calculateHri({ avg_temp: weather.avg_temp, solar: weather.solar, humidity: weather.humidity }, active.signal); if (!active.signal.aborted) setHri(result) }
    catch (e) { if (!active.signal.aborted) setHriError(e instanceof Error ? e.message : 'HRI недоступний.') }
    finally { if (!active.signal.aborted) setHriLoading(false) }
  }
  return <><div className="page-heading"><div><p className="eyebrow">ГЕОГРАФІЧНИЙ МОНІТОРИНГ</p><h1>Інтерактивна карта</h1><p className="subtitle">Населені пункти з MySQL · погода за підтвердженими координатами</p></div></div>
    <section className="provenance"><strong>Окремий географічний контекст</strong><p>Карта показує довідник населених пунктів. Історичні записи climate_data без координат до цих маркерів не приєднуються. HRI не є медичною ймовірністю.</p></section>
    <section className="panel"><div className="panel-body"><PlaceSearch onSelect={choose} /><div className="map-toolbar"><button className="secondary" disabled={loading} onClick={() => setQueryBounds({ ...bounds })}>Оновити видиму область</button><span>Маркери: {places.length} · до 200 за запит; перелік може бути неповним</span></div>
      {loading && <p role="status">Завантаження населених пунктів…</p>}{error && <p role="alert" className="inline-error">{error}</p>}{!loading && !error && places.length === 0 && <p>У вибраній області даних немає. Змініть масштаб або знайдіть місто.</p>}
      {tileError && <p className="quality-note">Картографічний фон недоступний. Скористайтеся пошуком і списком населених пунктів.</p>}
      <Suspense fallback={<p role="status">Завантаження картографічного модуля…</p>}><LeafletMap places={places} selected={selected} onSelect={choose} onBounds={setBounds} onTileError={() => setTileError(true)} /></Suspense>
      <details><summary>Доступний список населених пунктів — перші 20 з відповіді</summary><ul className="place-results">{places.slice(0, 20).map(place => <li key={place.id}><button className="secondary" onClick={() => choose(place)}>{place.name}<small>{place.lat.toFixed(4)}, {place.lon.toFixed(4)}</small></button></li>)}</ul></details>
    </div></section>
    {selected ? <><WeatherPanel key={selected.id} selectedPlace={selected} onWeather={value => { hriController.current?.abort(); setWeather(value); setHri(null); setHriError(''); setHriLoading(false) }} />
      <section className="panel"><div className="panel-body"><h2>HRI для {selected.name}</h2><p className="data-caption">Спочатку отримайте погоду для вибраних координат. Потім розрахуйте індекс за цими параметрами.</p><button disabled={!weather || hriLoading} onClick={analyze}>{hriLoading ? 'Обчислення…' : 'Розрахувати HRI для міста'}</button>{hriError && <p role="alert">{hriError}</p>}{hri && <p className="map-hri-result">Індекс HRI: <strong>{hri.hri.toFixed(3)}</strong> · 27 нечітких правил{hri.clipped && ' · входи обрізано до області моделі'}. Не медичний прогноз.</p>}</div></section></> : <p className="empty-hint">Виберіть маркер, місто зі списку або результат пошуку, щоб переглянути погоду та HRI.</p>}
  </>
}
