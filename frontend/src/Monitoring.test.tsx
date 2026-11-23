// Synthetic technical fixtures only. No medical observation or forecast.
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { HriPage } from './HriPage'
import { WeatherPanel } from './WeatherPanel'
import { MapPage } from './MapPage'
import { calculateHri, getWeather } from './monitoring-api'
import type { Place } from './monitoring-api'

vi.mock('./LeafletMap', () => ({ LeafletMap: ({ places, onSelect }: { places: Place[]; onSelect: (p: Place) => void }) => <div>{places.map(p => <button key={p.id} onClick={() => onSelect(p)}>Тестовий маркер {p.name}</button>)}</div> }))
afterEach(() => vi.unstubAllGlobals())
const place = { id: 1, name: 'Синтетичне місто', lat: 49, lon: 24, population: 100 }
const weather = { avg_temp: 20, solar: 180, humidity: 65, lat: 49, lon: 24, source: 'Open-Meteo', data_time: '2026-01-01T00:00:00Z', fetched_at: '2026-01-01T00:01:00Z', cached: false, quality_issues: ['conditions:model_not_station_observation'] }
const result = { hri: 0.5, inputs: { avg_temp: 20, solar: 180, humidity: 65 }, effective_inputs: { avg_temp: 20, solar: 180, humidity: 65 }, clipped: false, method: 'fuzzy_rules_27', medical_prediction: false }
const response = (data: unknown) => ({ ok: true, status: 200, json: async () => ({ data, meta: {} }) })
async function enter(values = ['20', '180', '65']) {
  for (const [index, label] of ['Температура, °C', 'Радіація, W/m²', 'Вологість, %'].entries()) {
    await userEvent.type(screen.getByLabelText(label), values[index])
  }
}

describe('HRI scenario', () => {
  it('rejects empty and invalid parameters before HTTP', async () => {
    const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher)
    render(<HriPage />)
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Перевірте числові')
    expect(screen.getByLabelText('Температура, °C')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText('Температура, °C')).toHaveAccessibleDescription(/Введіть число/)
    await enter(['20', '180', '150'])
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI' }))
    expect(screen.getByLabelText('Вологість, %')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText('Температура, °C')).not.toHaveAttribute('aria-invalid')
    expect(fetcher).not.toHaveBeenCalled()
  })
  it('posts numeric parameters and displays index, effective inputs and medical limitation', async () => {
    const fetcher = vi.fn().mockResolvedValue(response({ ...result, clipped: true }))
    vi.stubGlobal('fetch', fetcher)
    render(<HriPage />); await enter()
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI' }))
    expect(await screen.findByLabelText('Числовий індекс HRI')).toHaveTextContent('0.500')
    expect(screen.getByText(/частину параметрів обрізано/)).toBeInTheDocument()
    expect(screen.getByText(/не є медично валідованою/)).toBeInTheDocument()
    expect(JSON.parse(fetcher.mock.lastCall?.[1].body)).toEqual(result.inputs)
    await userEvent.clear(screen.getByLabelText('Температура, °C'))
    expect(screen.queryByLabelText('Числовий індекс HRI')).not.toBeInTheDocument()
  })
  it('shows a provider failure without invented index', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }))
    render(<HriPage />); await enter()
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('тимчасово недоступне')
    expect(screen.queryByLabelText('Числовий індекс HRI')).not.toBeInTheDocument()
  })
  it('ignores a stale response after input edit', async () => {
    let resolve: (v: unknown) => void = () => {}
    vi.stubGlobal('fetch', vi.fn(() => new Promise(r => { resolve = r })))
    render(<HriPage />); await enter()
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI' }))
    await userEvent.clear(screen.getByLabelText('Температура, °C'))
    resolve(response(result))
    await waitFor(() => expect(screen.queryByLabelText('Числовий індекс HRI')).not.toBeInTheDocument())
  })
  it('can fill parameters from explicit city weather request', async () => {
    const fetcher = vi.fn((url: string) => Promise.resolve(response(url.includes('/places/search') ? [place] : weather)))
    vi.stubGlobal('fetch', fetcher)
    render(<HriPage />)
    await userEvent.type(screen.getByLabelText('Населений пункт'), 'місто')
    await userEvent.click(screen.getByRole('button', { name: 'Знайти місто' }))
    await userEvent.click(await screen.findByRole('button', { name: /Синтетичне місто/ }))
    await userEvent.click(screen.getByRole('button', { name: 'Отримати погоду' }))
    await screen.findByText('Weather data by Open-Meteo.com')
    expect(screen.getByLabelText('Температура, °C')).toHaveValue(20)
    expect(fetcher.mock.lastCall?.[0]).toContain('lat=49&lon=24')
  })
})

describe('Weather and map states', () => {
  it('accepts explicitly entered coordinates without inventing a city or reading MySQL', async () => {
    const fetcher = vi.fn().mockResolvedValue(response(weather)); vi.stubGlobal('fetch', fetcher)
    render(<WeatherPanel />)
    await userEvent.click(screen.getByText('Погода за введеними координатами'))
    await userEvent.type(screen.getByLabelText('Широта, °'), '49')
    await userEvent.type(screen.getByLabelText('Довгота, °'), '24')
    await userEvent.click(screen.getByRole('button', { name: 'Використати координати' }))
    expect(screen.getByText('Введені координати', { exact: true })).toBeInTheDocument()
    expect(fetcher).not.toHaveBeenCalled()
    await userEvent.click(screen.getByRole('button', { name: 'Отримати погоду' }))
    await screen.findByText('Weather data by Open-Meteo.com')
    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(fetcher.mock.lastCall?.[0]).toContain('/weather?lat=49&lon=24')
  })
  it('does not invent weather before selection and shows empty search', async () => {
    const fetcher = vi.fn().mockResolvedValue(response([])); vi.stubGlobal('fetch', fetcher)
    render(<WeatherPanel />)
    expect(fetcher).not.toHaveBeenCalled()
    expect(screen.getByText(/Погодних значень до запиту немає/)).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Населений пункт'), 'місто')
    await userEvent.click(screen.getByRole('button', { name: 'Знайти місто' }))
    expect(await screen.findByText(/Населених пунктів не знайдено/)).toBeInTheDocument()
  })
  it('shows weather timestamps and source after selecting a marker, then computes HRI', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve(response(url.includes('/places?') ? [place] : url.includes('/weather?') ? weather : result))))
    render(<MapPage />)
    await userEvent.click(await screen.findByRole('button', { name: /Тестовий маркер/ }))
    expect(screen.getByRole('button', { name: 'Розрахувати HRI для міста' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: 'Отримати погоду' }))
    await screen.findByText('Weather data by Open-Meteo.com')
    expect(screen.getByText(/Час показників:/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Розрахувати HRI для міста' }))
    expect(await screen.findByText('0.500')).toBeInTheDocument()
  })
  it('shows map empty state and bounded request', async () => {
    const fetcher = vi.fn().mockResolvedValue(response([])); vi.stubGlobal('fetch', fetcher)
    render(<MapPage />)
    expect(await screen.findByText(/У вибраній області даних немає/)).toBeInTheDocument()
    expect(fetcher.mock.lastCall?.[0]).toContain('limit=200')
  })
  it('rejects malformed weather and a medically mislabelled HRI response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ ...weather, avg_temp: Infinity })))
    await expect(getWeather(place)).rejects.toThrow('Некоректні погодні')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ ...result, medical_prediction: true })))
    await expect(calculateHri(result.inputs)).rejects.toThrow('Некоректний результат HRI')
  })
})
