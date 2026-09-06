import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet marker icons in React/Vite
delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function App() {
  // Temporary locations
  const ambulancePosition = [13.0827, 80.2707]
  const hospitalPosition = [13.0674, 80.2376]

  // Temporary route
  const route = [
    [13.0827, 80.2707],
    [13.0785, 80.2640],
    [13.0740, 80.2570],
    [13.0700, 80.2490],
    [13.0674, 80.2376],
  ]

  // Temporary route information
  const distance = '6.8 km'
  const eta = '14 min'
  const traffic = 'Moderate'

  return (
    <div
      style={{
        height: '100vh',
        width: '100%',
        position: 'relative',
      }}
    >
      {/* Information Panel */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          zIndex: 1000,
          background: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.25)',
          width: '280px',
          fontFamily: 'Arial',
        }}
      >
        <h2 style={{ marginTop: 0 }}>
          🚑 Ambulance Route
        </h2>

        <p>
          <strong>Destination:</strong> 🏥 Hospital
        </p>

        <hr />

        <p>
          📏 <strong>Distance:</strong> {distance}
        </p>

        <p>
          ⏱️ <strong>ETA:</strong> {eta}
        </p>

        <p>
          🚦 <strong>Traffic:</strong> {traffic}
        </p>

        <hr />

        <p>
          🟢 <strong>Status:</strong> Route Active
        </p>
      </div>

      {/* Map */}
      <MapContainer
        center={ambulancePosition}
        zoom={13}
        style={{
          height: '100%',
          width: '100%',
        }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Ambulance */}
        <Marker position={ambulancePosition}>
          <Popup>
            🚑 <strong>Ambulance</strong>
            <br />
            Current Location
          </Popup>
        </Marker>

        {/* Hospital */}
        <Marker position={hospitalPosition}>
          <Popup>
            🏥 <strong>Hospital</strong>
            <br />
            Destination
          </Popup>
        </Marker>

        {/* Temporary A* route */}
        <Polyline
          positions={route}
          pathOptions={{
            color: 'red',
            weight: 6,
          }}
        />
      </MapContainer>
    </div>
  )
}

export default App
