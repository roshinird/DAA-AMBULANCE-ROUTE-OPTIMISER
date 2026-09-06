import L from 'leaflet'
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
} from 'react-leaflet'

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
  const ambulancePosition = [13.0827, 80.2707]
  const hospitalPosition = [13.0674, 80.2376]

  const route = [
    [13.0827, 80.2707],
    [13.0785, 80.2640],
    [13.0740, 80.2570],
    [13.0700, 80.2490],
    [13.0674, 80.2376],
  ]

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
