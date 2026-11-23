import { useEffect, useRef } from 'react'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { Observation } from './api'

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])
export function ObservationChart({ rows }: { rows: Observation[] }) {
  const element = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!element.current) return
    const chart = echarts.init(element.current)
    const style = getComputedStyle(element.current)
    const ink = style.getPropertyValue('--color-muted').trim() || '#52675f'
    const primary = style.getPropertyValue('--color-primary').trim() || '#1c6254'
    chart.setOption({
      animation: false,
      textStyle: { fontFamily: 'system-ui, sans-serif', color: ink, fontSize: 13 },
      color: [primary], grid: { left: 48, right: 24, top: 32, bottom: 45 },
      tooltip: { trigger: 'axis', renderMode: 'richText' },
      xAxis: { type: 'category', data: rows.map(r => `${r.year ?? '—'}-${String(r.month ?? '—').padStart(2, '0')}`), axisLabel: { hideOverlap: true, color: ink }, axisLine: { lineStyle: { color: ink } } },
      yAxis: { type: 'value', name: '°C', axisLabel: { color: ink }, splitLine: { lineStyle: { color: '#e5ece7', type: 'dashed' } } },
      series: [{ name: 'Середня температура', type: 'line', connectNulls: false,
        data: rows.map(r => r.avg_temp), showSymbol: true, lineStyle: { width: 2 } }],
    })
    const observer = new ResizeObserver(() => chart.resize())
    observer.observe(element.current)
    return () => { observer.disconnect(); chart.dispose() }
  }, [rows])
  return <div ref={element} className="chart" role="img" aria-label="Графік середньої температури; точні значення наведено в таблиці" />
}
