import { useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, useMapEvents } from 'react-leaflet'
import type { Place } from './monitoring-api'
import 'leaflet/dist/leaflet.css'

export type Bounds = { south: number; north: number; west: number; east: number }
function Viewport({ selected, onBounds }: { selected: Place | null; onBounds: (bounds: Bounds) => void }) {
  const map = useMap()
  useEffect(() => { if (selected) map.flyTo([selected.lat, selected.lon], 11) }, [map, selected])
  useMapEvents({ moveend() {
    const bounds = map.getBounds()
    onBounds({ south: Math.max(-90, bounds.getSouth()), north: Math.min(90, bounds.getNorth()), west: Math.max(-180, bounds.getWest()), east: Math.min(180, bounds.getEast()) })
  } })
  return null
}
export function LeafletMap({ places, selected, onSelect, onBounds, onTileError }: { places: Place[]; selected: Place | null; onSelect: (place: Place) => void; onBounds: (bounds: Bounds) => void; onTileError: () => void }) {
  const points = selected && !places.some(p => p.id === selected.id) ? [...places, selected] : places
  return <MapContainer center={[49, 31]} zoom={6} minZoom={3} maxZoom={16} className="leaflet-map" scrollWheelZoom={false}>
    <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' eventHandlers={{ tileerror: onTileError }} />
    <Viewport selected={selected} onBounds={onBounds} />
    {points.map(place => <CircleMarker key={place.id} center={[place.lat, place.lon]} radius={place.id === selected?.id ? 10 : 5} pathOptions={{ color: '#226b5b', fillOpacity: 0.7 }} eventHandlers={{ click: () => onSelect(place) }}>
      <Popup><strong>{place.name}</strong><p>{place.lat.toFixed(4)}, {place.lon.toFixed(4)}</p><button onClick={() => onSelect(place)}>Вибрати населений пункт</button></Popup>
    </CircleMarker>)}
  </MapContainer>
}
