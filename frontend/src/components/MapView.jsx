import L from 'leaflet'
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
} from 'react-leaflet'
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

function MapView() {
  const ambulancePosition = routeData.ambulance.position
  const hospitalPosition = routeData.hospital.position
  const route = routeData.route

  return (
    <MapContainer
      center={[13.075, 80.255]}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <Marker position={ambulancePosition} icon={ambulanceIcon}>
        <Popup>🚑 Ambulance</Popup>
      </Marker>

      <Marker position={hospitalPosition} icon={hospitalIcon}>
        <Popup>🏥 Hospital</Popup>
      </Marker>

      <Polyline
        positions={route}
        pathOptions={{
          color: 'red',
          weight: 6,
        }}
      />
    </MapContainer>
  )
}

export default MapView
