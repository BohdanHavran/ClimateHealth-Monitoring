// Synthetic fixtures for UI tests only; never served as real observations.
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, afterEach } from 'vitest'
import App from './App'
import { getObservations } from './api'
import { HistoryPanel } from './HistoryPanel'

vi.mock('./ObservationChart', () => ({ ObservationChart: () => <div>Тестова діаграма</div> }))
afterEach(() => vi.unstubAllGlobals())
const row = { id: 1, year: 2026, month: 1, avg_temp: 3, solar_irradiance: null, humidity: 60, quality_issues: ['solar_irradiance:missing'] }
const response = (data = [row], next: number | null = null) => ({ ok: true, json: async () => ({ data, meta: { next_after_id: next } }) })

describe('Historical observations', () => {
  it('keeps the dashboard preview small while retaining the full history', async () => {
    const records = Array.from({ length: 12 }, (_, index) => ({ ...row, id: index + 1 }))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(records)))
    const view = render(<HistoryPanel overview />)
    await screen.findByRole('table')
    expect(screen.getAllByRole('row')).toHaveLength(6)
    expect(screen.getByText(/Перші 5 з 12/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Усі спостереження →' })).toHaveAttribute('href', '#history')
    const expand = screen.getByRole('button', { name: 'Показати всі значення графіка в таблиці' })
    await userEvent.click(expand)
    expect(expand).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getAllByRole('row')).toHaveLength(13)
    await userEvent.click(expand)
    expect(screen.getAllByRole('row')).toHaveLength(6)
    view.unmount()
    render(<HistoryPanel />)
    await screen.findByRole('table')
    expect(screen.getAllByRole('row')).toHaveLength(13)
  })
  it('offers a keyboard skip link without changing the current route', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response()))
    render(<App />)
    await screen.findByRole('table')
    await userEvent.tab()
    expect(screen.getByRole('link', { name: 'Перейти до вмісту' })).toHaveFocus()
    await userEvent.keyboard('{Enter}')
    expect(screen.getByRole('main')).toHaveFocus()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Клімат у фокусі')
  })
  it('shows loading without invented data', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<App />)
    expect(screen.getByRole('status')).toHaveTextContent('Завантаження')
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })
  it('renders records and missing values with a provenance notice', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response()))
    render(<App />)
    expect(await screen.findByRole('table')).toBeInTheDocument()
    expect(screen.getByText('Немає даних')).toBeInTheDocument()
    expect(screen.getByText(/Територію та первинне джерело/)).toBeInTheDocument()
    expect(screen.getByText('Є зауваження')).toBeInTheDocument()
  })
  it('renders empty state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response([])))
    render(<App />)
    expect(await screen.findByText('Спостережень не знайдено')).toBeInTheDocument()
  })
  it('renders error and retries', async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValue(response())
    vi.stubGlobal('fetch', fetcher)
    render(<App />)
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Повторити' }))
    expect(await screen.findByRole('table')).toBeInTheDocument()
  })
  it('applies year filter and follows the server cursor', async () => {
    const fetcher = vi.fn().mockResolvedValue(response([row], 1))
    vi.stubGlobal('fetch', fetcher)
    render(<App />)
    await screen.findByRole('table')
    await userEvent.type(screen.getByLabelText('Рік спостережень'), '2026')
    await userEvent.click(screen.getByRole('button', { name: 'Застосувати' }))
    await waitFor(() => expect(fetcher.mock.lastCall?.[0]).toContain('year=2026'))
    await screen.findByRole('table')
    await userEvent.click(screen.getByRole('button', { name: 'Наступна →' }))
    await waitFor(() => expect(fetcher.mock.lastCall?.[0]).toContain('after_id=1'))
  })
  it('rejects malformed data and a repeating cursor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response([{ ...row, avg_temp: Infinity }])))
    await expect(getObservations('', 0, new AbortController().signal)).rejects.toThrow('Некоректна відповідь')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response([row], 1)))
    await expect(getObservations('', 1, new AbortController().signal)).rejects.toThrow('пагінація')
  })
})
