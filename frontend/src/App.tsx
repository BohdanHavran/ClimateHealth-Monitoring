import { lazy, Suspense, useEffect, useState } from 'react'
import { HistoryPanel } from './HistoryPanel'
import { HriPage } from './HriPage'
import { WeatherPanel } from './WeatherPanel'
import './styles.css'
import './monitoring.css'

const MapPage = lazy(() => import('./MapPage').then(module => ({ default: module.MapPage })))
const pages = ['dashboard', 'hri', 'map', 'history'] as const
type Page = typeof pages[number]
function readPage(): Page { const page = window.location.hash.slice(1); return pages.includes(page as Page) ? page as Page : 'dashboard' }

export default function App() {
  const [page, setPage] = useState<Page>(readPage)
  useEffect(() => { const update = () => setPage(readPage()); window.addEventListener('hashchange', update); return () => window.removeEventListener('hashchange', update) }, [])
  const links = [{ id: 'dashboard', label: 'Головна панель' }, { id: 'hri', label: 'HRI Analysis' }, { id: 'map', label: 'Інтерактивна карта' }, { id: 'history', label: 'Історичні дані' }]
  return <div className="app-shell"><header className="topbar"><a className="brand" href="#dashboard" aria-label="ClimateHealth — головна"><span className="brand-icon">C</span>ClimateHealth</a><span className="workspace">ДОСЛІДНИЦЬКИЙ ПРОСТІР</span><span className="read-only">MySQL · лише читання</span></header>
    <div className="workspace-layout"><aside><nav aria-label="Головна навігація"><p className="nav-label">МОНІТОРИНГ</p>{links.map(link => <a key={link.id} className={page === link.id ? 'nav-current' : 'nav-link'} href={'#' + link.id} aria-current={page === link.id ? 'page' : undefined}>{link.label}</a>)}</nav><div className="sidebar-note">Кліматичні умови<br/><strong>Дані перед висновками.</strong><p>Джерело, час і якість — передумови обґрунтованого аналізу.</p><span>ML-модель ще недоступна.</span></div></aside>
    <main>
      {page === 'dashboard' && <><div className="page-heading"><div><p className="eyebrow">CLIMATEHEALTH / ОГЛЯД</p><h1>Клімат у фокусі</h1><p className="subtitle">Поточні умови та історичний контекст — із прозорими джерелами.</p></div><a className="secondary page-link" href="#hri">Перейти до HRI →</a></div><WeatherPanel /><HistoryPanel /></>}
      {page === 'hri' && <HriPage />}
      {page === 'map' && <Suspense fallback={<p role="status">Завантаження карти…</p>}><MapPage /></Suspense>}
      {page === 'history' && <><h1 className="sr-only">Історичні кліматичні дані</h1><HistoryPanel /></>}
      <footer>ClimateHealth · Дослідницька система моніторингу. HRI не є медично підтвердженою ймовірністю захворювання.</footer>
    </main></div></div>
}
