import { useEffect, useState } from 'react'
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

function MapView({ route, traffic }) {
  const [ambulancePosition, setAmbulancePosition] = useState(route[0])

  useEffect(() => {
    if (!route || route.length < 2) {
      return
    }

    let segmentIndex = 0
    let animationFrame
    let segmentStartTime = null

    const segmentDuration = 4000

    const animate = (timestamp) => {
      if (!segmentStartTime) {
        segmentStartTime = timestamp
      }

      const elapsed = timestamp - segmentStartTime
      const progress = Math.min(elapsed / segmentDuration, 1)

      const start = route[segmentIndex]
      const end = route[segmentIndex + 1]

      const latitude =
        start[0] + (end[0] - start[0]) * progress

      const longitude =
        start[1] + (end[1] - start[1]) * progress

      setAmbulancePosition([latitude, longitude])

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      } else {
        segmentIndex += 1
        segmentStartTime = null

        if (segmentIndex < route.length - 1) {
          animationFrame = requestAnimationFrame(animate)
        }
      }
    }

    setAmbulancePosition(route[0])
    animationFrame = requestAnimationFrame(animate)

    return () => {
      cancelAnimationFrame(animationFrame)
    }
  }, [route])

  const hospitalPosition = routeData.hospital.position

  const trafficColors = {
    Low: 'green',
    Moderate: 'orange',
    Heavy: 'red',
  }

  const routeColor = trafficColors[traffic] || 'red'

  return (
    <MapContainer
      center={routeData.ambulance.position}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <Marker
        position={ambulancePosition}
        icon={ambulanceIcon}
      >
        <Popup>
          🚑 <strong>Ambulance</strong>
          <br />
          Current Location
        </Popup>
      </Marker>

      <Marker
        position={hospitalPosition}
        icon={hospitalIcon}
      >
        <Popup>
          🏥 <strong>Hospital</strong>
          <br />
          Destination
        </Popup>
      </Marker>

      <Polyline
        positions={route}
        pathOptions={{
          color: routeColor,
          weight: 6,
        }}
      />

      <div className="traffic-legend">
        <h3>🚦 Traffic</h3>

        <div>
          <span className="legend-line low"></span>
          Low
        </div>

        <div>
          <span className="legend-line moderate"></span>
          Moderate
        </div>

        <div>
          <span className="legend-line heavy"></span>
          Heavy
        </div>
      </div>
    </MapContainer>
  )
}

export default MapView