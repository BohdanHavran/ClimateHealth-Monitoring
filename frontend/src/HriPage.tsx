import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { calculateHri } from './monitoring-api'
import type { HriResult, Weather } from './monitoring-api'
import { WeatherPanel } from './WeatherPanel'

export function HriPage() {
  const [values, setValues] = useState({ avg_temp: '', solar: '', humidity: '' })
  const [result, setResult] = useState<HriResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [invalidFields, setInvalidFields] = useState<string[]>([])
  const [origin, setOrigin] = useState('Ручне введення')
  const controller = useRef<AbortController | null>(null)
  useEffect(() => () => controller.current?.abort(), [])
  const fields = [
    { key: 'avg_temp' as const, label: 'Температура, °C', min: -100, max: 70 },
    { key: 'solar' as const, label: 'Радіація, W/m²', min: 0, max: 1600 },
    { key: 'humidity' as const, label: 'Вологість, %', min: 0, max: 100 },
  ]
  function resetResult() { controller.current?.abort(); setResult(null); setError(''); setInvalidFields([]); setLoading(false) }
  function fromWeather(weather: Weather) {
    resetResult(); setValues({ avg_temp: String(weather.avg_temp), solar: String(weather.solar), humidity: String(weather.humidity) })
    setOrigin(`Open-Meteo · ${weather.lat.toFixed(4)}, ${weather.lon.toFixed(4)} · час показників ${new Date(weather.data_time).toLocaleString('uk-UA')} · модельні значення`)
  }
  async function calculate(event: FormEvent) {
    event.preventDefault(); resetResult()
    const numbers = { avg_temp: Number(values.avg_temp), solar: Number(values.solar), humidity: Number(values.humidity) }
    const invalid = fields.filter(f => values[f.key].trim() === '' || !Number.isFinite(numbers[f.key]) || numbers[f.key] < f.min || numbers[f.key] > f.max).map(f => f.key)
    if (invalid.length) { setInvalidFields(invalid); setError('Перевірте числові значення та допустимі межі.'); return }
    const active = new AbortController(); controller.current = active
    setLoading(true)
    try { const value = await calculateHri(numbers, active.signal); if (!active.signal.aborted) setResult(value) }
    catch (e) { if (!active.signal.aborted) setError(e instanceof Error ? e.message : 'Розрахунок недоступний.') }
    finally { if (!active.signal.aborted) setLoading(false) }
  }
  return <><div className="page-heading"><div><p className="eyebrow">НЕЧІТКЕ МОДЕЛЮВАННЯ</p><h1>HRI Analysis</h1><p className="subtitle">27 правил · індекс від 0 до 1 · без нейромережевого прогнозу</p></div></div>
    <section className="provenance"><strong>Індекс умов, а не ймовірність захворювання</strong><p>HRI відображає результат наявних нечітких правил. Він не є медично валідованою оцінкою здоров’я або підставою для клінічного рішення.</p></section>
    <div className="hri-layout"><section className="panel"><div className="panel-heading"><div><h2>Параметри розрахунку</h2><p>Заповніть усі поля або отримайте погоду нижче</p></div></div><form className="panel-body hri-form" onSubmit={calculate} noValidate>
      {fields.map(field => <div className="hri-field" key={field.key}><label htmlFor={'hri-' + field.key}>{field.label}</label><input id={'hri-' + field.key} aria-invalid={invalidFields.includes(field.key) || undefined} aria-describedby={'hri-help-' + field.key} type="number" step="any" min={field.min} max={field.max} required value={values[field.key]} onChange={e => { resetResult(); setOrigin('Ручне введення'); setValues(v => ({ ...v, [field.key]: e.target.value })) }} /><small id={'hri-help-' + field.key}>{invalidFields.includes(field.key) && 'Введіть число в допустимому діапазоні. '}Межі: {field.min}…{field.max}</small></div>)}
      <p className="data-caption">Джерело параметрів: {origin}</p><button disabled={loading}>{loading ? 'Обчислення…' : 'Розрахувати HRI'}</button>
      {loading && <p role="status">Виконуємо розрахунок Flask HRI…</p>}{error && <p role="alert" className="inline-error">{error}</p>}
    </form></section>
    <section className="panel result-panel" aria-label="Результат HRI"><div className="panel-heading"><h2>Результат аналізу</h2></div><div className="panel-body">{result ? <><output className="hri-number" aria-label="Числовий індекс HRI">{result.hri.toFixed(3)}</output><meter min="0" max="1" value={result.hri} aria-label="Шкала індексу HRI" /><div className="meter-labels"><span>0</span><span>1</span></div><p>Метод: 27 нечітких правил.</p><p className="quality-note">{result.clipped ? 'Увага: частину параметрів обрізано до області визначення моделі.' : 'Усі параметри перебувають у межах області моделі.'}</p><dl className="effective-inputs"><dt>Використана температура</dt><dd>{result.effective_inputs.avg_temp} °C</dd><dt>Використана радіація</dt><dd>{result.effective_inputs.solar} W/m²</dd><dt>Використана вологість</dt><dd>{result.effective_inputs.humidity} %</dd></dl></> : <p className="empty-hint">Результат з’явиться після успішного розрахунку. До цього значення індексу не підставляється.</p>}</div></section></div>
    <WeatherPanel onWeather={fromWeather} /><section className="panel"><div className="panel-body"><h2>Як інтерпретувати параметри</h2><p className="data-caption">Область нечіткої моделі: температура −5…35 °C, радіація 60…300 W/m², вологість 30…100 %. Фізично допустимі входи поза цією областю обрізаються; ефективні значення показано біля результату. Поточні модельні показники не тотожні станційним вимірюванням; область застосування правил потребує наукової валідації.</p></div></section>
  </>
}
