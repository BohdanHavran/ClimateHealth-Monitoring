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
    chart.setOption({
      color: ['#27806f'], grid: { left: 50, right: 24, top: 24, bottom: 60 },
      tooltip: { trigger: 'axis', renderMode: 'richText' },
      xAxis: { type: 'category', data: rows.map(r => `${r.year ?? '—'}-${String(r.month ?? '—').padStart(2, '0')}`), axisLabel: { rotate: 35 } },
      yAxis: { type: 'value', name: '°C' },
      series: [{ name: 'Середня температура', type: 'line', connectNulls: false,
        data: rows.map(r => r.avg_temp), showSymbol: true, lineStyle: { width: 2 } }],
    })
    const observer = new ResizeObserver(() => chart.resize())
    observer.observe(element.current)
    return () => { observer.disconnect(); chart.dispose() }
  }, [rows])
  return <div ref={element} className="chart" role="img" aria-label="Графік середньої температури; точні значення наведено в таблиці" />
}
