import { lazy, Suspense, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { getObservations } from './api'
import type { ObservationPage } from './api'
const ObservationChart = lazy(() => import('./ObservationChart').then(module => ({ default: module.ObservationChart })))
import './styles.css'

const display = (value: number | null) => value === null ? 'Немає даних' : new Intl.NumberFormat('uk-UA', { maximumFractionDigits: 2 }).format(value)

export function HistoryPanel({ overview = false }: { overview?: boolean }) {
  const [draftYear, setDraftYear] = useState('')
  const [year, setYear] = useState('')
  const [cursors, setCursors] = useState([0])
  const [revision, setRevision] = useState(0)
  const [page, setPage] = useState<ObservationPage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState(false)
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
  return <section id="observations" className="history-panel"><div className="breadcrumb">Моніторинг / Історичні дані</div><div className="page-heading"><div><p className="eyebrow">КЛІМАТИЧНІ СПОСТЕРЕЖЕННЯ</p><h2 className="history-title">Історія у вимірах</h2><p className="subtitle">Перегляд збережених показників і їхньої якості.</p></div><span className="source-chip">MySQL · climate_data</span></div>
    <section className="provenance" aria-label="Походження даних"><strong>Контекст має значення</strong><p>Територію та первинне джерело записів у базі не підтверджено. Ці значення не є медичними спостереженнями або прогнозом здоров’я. Пропуски не заповнюються автоматично.</p></section>
    <form className="filter-bar" onSubmit={applyFilter}><label htmlFor="year">Рік спостережень<input id="year" type="number" min="1800" max="2200" step="1" value={draftYear} placeholder="Усі роки" onChange={e => setDraftYear(e.target.value)} /></label><button type="submit" disabled={loading}>Застосувати</button><button className="secondary" type="button" disabled={loading} onClick={() => setRevision(r => r + 1)}>Оновити</button><span className="filter-note">До 50 записів на сторінку · порядок за ID</span></form>
    {loading && <div className="state" role="status">Завантаження спостережень…</div>}
    {error && <div className="state error" role="alert">{error}<button className="secondary" onClick={() => setRevision(r => r + 1)}>Повторити</button></div>}
    {!loading && !error && page && (page.data.length === 0 ? <div className="state"><h2>Спостережень не знайдено</h2><p>Для вибраного періоду в базі немає записів. Змініть рік або скиньте фільтр.</p></div> : <>
      <div className="stats"><div><span>Записів на сторінці</span><strong>{page.data.length}</strong></div><div><span>Записів із зауваженнями</span><strong>{page.data.filter(r => r.quality_issues.length > 0).length}</strong></div><div><span>Показники</span><strong>°C <small>/</small> W/m² <small>/</small> %</strong></div></div>
      {page.meta.received_at && <p className="data-caption">Отримано з MySQL: {new Date(page.meta.received_at).toLocaleString('uk-UA')}. Час первинного внесення та походження спостережень невідомі.</p>}
      <section className="panel"><div className="panel-heading"><div><h2>Температурний профіль</h2><p>Поточна сторінка · лінія з’єднує записи в порядку ID, не доводить безперервність часового ряду</p></div><span className="legend"><i/>Середня температура</span></div><Suspense fallback={<p role="status">Завантаження графіка…</p>}><ObservationChart rows={page.data}/></Suspense>{overview && <div className="chart-alternative"><button type="button" className="secondary" aria-expanded={expanded} aria-controls="observation-values" onClick={() => setExpanded(value => !value)}>{expanded ? 'Згорнути значення графіка' : 'Показати всі значення графіка в таблиці'}</button></div>}</section>
      <section className="panel"><div className="panel-heading"><div><h2>{overview ? 'Короткий перегляд спостережень' : 'Збережені спостереження'}</h2><p>{overview ? `Перші ${(expanded ? page.data.length : Math.min(5, page.data.length))} з ${page.data.length} записів поточної сторінки · графік вище охоплює всю сторінку` : 'Первинні значення без заміни пропусків або обрізання меж'}</p></div>{overview && <a className="text-link" href="#history">Усі спостереження →</a>}</div><div className="table-scroll" tabIndex={0} role="region" aria-label="Таблиця спостережень, прокручується горизонтально"><table id="observation-values"><caption className="sr-only">Історичні кліматичні спостереження з MySQL</caption><thead><tr><th scope="col">ID</th><th scope="col">Рік / місяць</th><th scope="col">Температура, °C</th><th scope="col">Радіація, W/m²</th><th scope="col">Вологість, %</th><th scope="col">Якість запису</th></tr></thead><tbody>{(overview && !expanded ? page.data.slice(0, 5) : page.data).map(row => <tr key={row.id}><td>{row.id}</td><td>{display(row.year)} / {display(row.month)}</td><td>{display(row.avg_temp)}</td><td>{display(row.solar_irradiance)}</td><td>{display(row.humidity)}</td><td>{row.quality_issues.length ? <span className="quality warning">Є зауваження<details><summary>Деталі перевірки</summary>{row.quality_issues.join(', ')}</details></span> : <span className="quality">Базові перевірки пройдено</span>}</td></tr>)}</tbody></table></div></section>
    </>)}
    <nav className="pagination" aria-label="Сторінки спостережень"><button className="secondary" disabled={loading || cursors.length === 1} onClick={() => setCursors(c => c.slice(0, -1))}>← Попередня</button><span>Сторінка {cursors.length}</span><button className="secondary" disabled={loading || !page?.meta.next_after_id} onClick={() => { const next = page?.meta.next_after_id; if (next) setCursors(c => [...c, next]) }}>Наступна →</button></nav></section>
}
