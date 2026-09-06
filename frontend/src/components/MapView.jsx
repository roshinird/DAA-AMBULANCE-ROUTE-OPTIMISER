import { useEffect, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  CircleMarker,
  Popup,
} from 'react-leaflet'
import L from 'leaflet'
import { routeData } from '../data'

const ambulanceIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="ambulance-marker">🚑</div>',
  iconSize: [42, 42],
  iconAnchor: [21, 21],
})

const hospitalIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="hospital-marker">🏥</div>',
  iconSize: [42, 42],
  iconAnchor: [21, 21],
})

function MapView({ route, traffic }) {
  const [ambulancePosition, setAmbulancePosition] = useState(
    routeData.ambulance.position
  )

  const trafficColor =
    traffic === 'Heavy'
      ? 'red'
      : traffic === 'Moderate'
        ? 'orange'
        : 'green'

  useEffect(() => {
    if (!route || route.length < 2) return

    let segmentIndex = 0
    let animationFrame = null
    let segmentStartTime = null
    let cancelled = false

    const segmentDuration = 4000

    const animate = (timestamp) => {
      if (cancelled) return

      if (segmentStartTime === null) {
        segmentStartTime = timestamp
      }

      const progress = Math.min(
        (timestamp - segmentStartTime) / segmentDuration,
        1
      )

      const start = route[segmentIndex]
      const end = route[segmentIndex + 1]

      const latitude =
        start[0] + (end[0] - start[0]) * progress

      const longitude =
        start[1] + (end[1] - start[1]) * progress

      setAmbulancePosition([
        latitude,
        longitude,
      ])

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
        return
      }

      segmentIndex += 1
      segmentStartTime = null

      if (segmentIndex < route.length - 1) {
        animationFrame = requestAnimationFrame(animate)
        return
      }

      // =====================================
      // DESTINATION REACHED
      // =====================================

      const destination = route[route.length - 1]

      // Keep ambulance at destination
      setAmbulancePosition([
        destination[0],
        destination[1],
      ])

      // Do not start another animation
      animationFrame = null
    }

    animationFrame = requestAnimationFrame(animate)

    return () => {
      cancelled = true

      if (animationFrame !== null) {
        cancelAnimationFrame(animationFrame)
      }
    }
  }, [])

  // Final destination
  const destination = route[route.length - 1]

  // Check whether ambulance reached destination
  const hasArrived =
    ambulancePosition[0] === destination[0] &&
    ambulancePosition[1] === destination[1]

  // Move ambulance slightly visually after arrival
  // so both ambulance and hospital remain visible.
  const displayedAmbulancePosition = hasArrived
    ? [
        ambulancePosition[0] + 0.0002,
        ambulancePosition[1],
      ]
    : ambulancePosition

  return (
    <MapContainer
      center={routeData.ambulance.position}
      zoom={13}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* OpenStreetMap */}
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* =====================================
          ROUTE
          ===================================== */}

      <Polyline
        positions={route}
        pathOptions={{
          color: trafficColor,
          weight: 7,
          opacity: 0.85,
        }}
      />

      {/* =====================================
          HOSPITAL
          ===================================== */}

      <Marker
        position={routeData.hospital.position}
        icon={hospitalIcon}
        zIndexOffset={1000}
      >
        <Popup>
          🏥 Hospital
        </Popup>
      </Marker>

      {/* =====================================
          AMBULANCE
          ===================================== */}

      <Marker
        position={displayedAmbulancePosition}
        icon={ambulanceIcon}
        zIndexOffset={2000}
      >
        <Popup>
          🚑 Ambulance
        </Popup>
      </Marker>

      {/* =====================================
          STARTING POINT
          ===================================== */}

      <CircleMarker
        center={route[0]}
        radius={6}
        pathOptions={{
          color: 'white',
          fillColor: 'green',
          fillOpacity: 1,
          weight: 2,
        }}
      />

      {/* =====================================
          DESTINATION
          ===================================== */}

      <CircleMarker
        center={route[route.length - 1]}
        radius={7}
        pathOptions={{
          color: 'white',
          fillColor: 'red',
          fillOpacity: 1,
          weight: 2,
        }}
      />

      {/* =====================================
          TRAFFIC LEGEND
          ===================================== */}

      <div className="traffic-legend">
        <h3>🚦 Traffic</h3>

        <div>
          <span className="legend-line low"></span>
          <span>Low</span>
        </div>

        <div>
          <span className="legend-line moderate"></span>
          <span>Moderate</span>
        </div>

        <div>
          <span className="legend-line heavy"></span>
          <span>Heavy</span>
        </div>
      </div>
    </MapContainer>
  )
}

export default MapView
