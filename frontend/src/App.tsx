import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { getObservations } from './api'
import type { ObservationPage } from './api'
import { ObservationChart } from './ObservationChart'
import './styles.css'

const display = (value: number | null) => value === null ? 'Немає даних' : new Intl.NumberFormat('uk-UA', { maximumFractionDigits: 2 }).format(value)

export default function App() {
  const [draftYear, setDraftYear] = useState('')
  const [year, setYear] = useState('')
  const [cursors, setCursors] = useState([0])
  const [revision, setRevision] = useState(0)
  const [page, setPage] = useState<ObservationPage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const cursor = cursors[cursors.length - 1]
  useEffect(() => {
    const controller = new AbortController()
    let active = true
    const timeout = window.setTimeout(() => controller.abort(), 12000)
    setLoading(true); setError(''); setPage(null)
    getObservations(year, cursor, controller.signal).then(result => {
      if (active) setPage(result)
    }).catch(() => {
      if (active) setError(controller.signal.aborted ? 'Час очікування вичерпано. Повторіть запит.' : 'Не вдалося завантажити дані. Перевірте доступність Flask і MySQL.')
    }).finally(() => { if (active) setLoading(false) })
    return () => { active = false; window.clearTimeout(timeout); controller.abort() }
  }, [year, cursor, revision])
  function applyFilter(event: FormEvent) {
    event.preventDefault(); setYear(draftYear); setCursors([0]); setRevision(r => r + 1)
  }
  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="/" aria-label="ClimateHealth — головна"><span className="brand-icon">C</span>ClimateHealth</a><span className="workspace">ДОСЛІДНИЦЬКИЙ ПРОСТІР</span><span className="read-only">Лише читання</span></header>
    <div className="workspace-layout"><aside><p className="nav-label">МОНІТОРИНГ</p><a className="nav-current" href="#observations" aria-current="page">Історичні спостереження</a><div className="sidebar-note">Кліматичні умови<br/><strong>Дані перед висновками.</strong><p>Перевіряйте походження й повноту кожного набору.</p></div></aside>
    <main id="observations"><div className="breadcrumb">Моніторинг / Історичні дані</div><div className="page-heading"><div><p className="eyebrow">КЛІМАТИЧНІ СПОСТЕРЕЖЕННЯ</p><h1>Історія у вимірах</h1><p className="subtitle">Перегляд збережених показників і їхньої якості.</p></div><span className="source-chip">MySQL · climate_data</span></div>
    <section className="provenance" aria-label="Походження даних"><strong>Контекст має значення</strong><p>Територію та первинне джерело записів у базі не підтверджено. Ці значення не є медичними спостереженнями або прогнозом здоров’я. Пропуски не заповнюються автоматично.</p></section>
    <form className="filter-bar" onSubmit={applyFilter}><label htmlFor="year">Рік спостережень<input id="year" type="number" min="1800" max="2200" step="1" value={draftYear} placeholder="Усі роки" onChange={e => setDraftYear(e.target.value)} /></label><button type="submit" disabled={loading}>Застосувати</button><button className="secondary" type="button" disabled={loading} onClick={() => setRevision(r => r + 1)}>Оновити</button><span className="filter-note">До 50 записів на сторінку · порядок за ID</span></form>
    {loading && <div className="state" role="status">Завантаження спостережень…</div>}
    {error && <div className="state error" role="alert">{error}<button className="secondary" onClick={() => setRevision(r => r + 1)}>Повторити</button></div>}
    {!loading && !error && page && (page.data.length === 0 ? <div className="state"><h2>Спостережень не знайдено</h2><p>Для вибраного періоду в базі немає записів. Змініть рік або скиньте фільтр.</p></div> : <>
      <div className="stats"><div><span>Записів на сторінці</span><strong>{page.data.length}</strong></div><div><span>Записів із зауваженнями</span><strong>{page.data.filter(r => r.quality_issues.length > 0).length}</strong></div><div><span>Показники</span><strong>°C <small>/</small> W/m² <small>/</small> %</strong></div></div>
      <section className="panel"><div className="panel-heading"><div><h2>Температурний профіль</h2><p>Поточна сторінка · лінія з’єднує записи в порядку ID, не доводить безперервність часового ряду</p></div><span className="legend"><i/>Середня температура</span></div><ObservationChart rows={page.data}/></section>
      <section className="panel"><div className="panel-heading"><div><h2>Збережені спостереження</h2><p>Первинні значення без заміни пропусків або обрізання меж</p></div></div><div className="table-scroll"><table><caption className="sr-only">Історичні кліматичні спостереження з MySQL</caption><thead><tr><th>ID</th><th>Рік / місяць</th><th>Температура, °C</th><th>Радіація, W/m²</th><th>Вологість, %</th><th>Якість запису</th></tr></thead><tbody>{page.data.map(row => <tr key={row.id}><td>{row.id}</td><td>{display(row.year)} / {display(row.month)}</td><td>{display(row.avg_temp)}</td><td>{display(row.solar_irradiance)}</td><td>{display(row.humidity)}</td><td>{row.quality_issues.length ? <span className="quality warning" title={row.quality_issues.join(', ')}>Є зауваження</span> : <span className="quality">Базові перевірки пройдено</span>}</td></tr>)}</tbody></table></div></section>
    </>)}
    <nav className="pagination" aria-label="Сторінки спостережень"><button className="secondary" disabled={loading || cursors.length === 1} onClick={() => setCursors(c => c.slice(0, -1))}>← Попередня</button><span>Сторінка {cursors.length}</span><button className="secondary" disabled={loading || !page?.meta.next_after_id} onClick={() => { const next = page?.meta.next_after_id; if (next) setCursors(c => [...c, next]) }}>Наступна →</button></nav><footer>ClimateHealth · Дослідницька система моніторингу. Медична точність не встановлена.</footer></main></div>
  </div>
}
