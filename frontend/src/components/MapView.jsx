import L from 'leaflet'
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet'
import { routeData } from '../data'

const ambulanceIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="ambulance-marker">🚑</div>',
  iconSize: [40, 40],
  iconAnchor: [20, 20],
})

const hospitalIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="hospital-marker">🏥</div>',
  iconSize: [40, 40],
  iconAnchor: [20, 20],
})

function MapView({ route, traffic }) {
  const ambulancePosition = routeData.ambulance.position
  const hospitalPosition = routeData.hospital.position

  const trafficColors = {
    Low: 'green',
    Moderate: 'orange',
    Heavy: 'red',
  }

  const routeColor = trafficColors[traffic] || 'red'

  return (
    <MapContainer
      center={ambulancePosition}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <Marker
        position={ambulancePosition}
        icon={ambulanceIcon}
      />

      <Marker
        position={hospitalPosition}
        icon={hospitalIcon}
      />

      <Polyline
        positions={route}
        pathOptions={{
          color: routeColor,
          weight: 6,
        }}
      />
    </MapContainer>
  )
}

export default MapView
