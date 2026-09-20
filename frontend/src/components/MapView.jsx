import { useEffect, useRef, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  CircleMarker,
  useMap,
} from 'react-leaflet'
import L from 'leaflet'
import {
  patientLocations,
  hospitals,
} from '../data'

const patientIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="patient-marker">🏠</div>',
  iconSize: [42, 42],
  iconAnchor: [21, 21],
})

const hospitalIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="hospital-marker">🏥</div>',
  iconSize: [42, 42],
  iconAnchor: [21, 21],
})

const ambulanceIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="ambulance-marker">🚑</div>',
  iconSize: [42, 42],
  iconAnchor: [21, 21],
})

const trafficSignalIcon = L.divIcon({
  className: 'custom-marker',
  html: '<div class="traffic-signal-marker">🚦</div>',
  iconSize: [70, 70],
  iconAnchor: [35, 35],
})

function RouteViewport({ route }) {
  const map = useMap()

  useEffect(() => {
    if (!route || route.length < 2) {
      return
    }

    const bounds = L.latLngBounds(route)

    map.fitBounds(bounds, {
      padding: [60, 60],
      maxZoom: 15,
    })
  }, [map, route])

  return null
}

function MapView({
  route,
  traffic,
  selectedPatient,
  selectedHospital,
  routeStarted,
  routeVersion,
}) {
  const [
    ambulancePosition,
    setAmbulancePosition,
  ] = useState(null)

  const [
    hasArrived,
    setHasArrived,
  ] = useState(false)

  const [
    alertShown,
    setAlertShown,
  ] = useState(false)

  const trafficSignalRef = useRef(null)

  const trafficColor =
    traffic === 'Heavy Traffic'
      ? 'red'
      : 'green'

  /*
   * The special traffic signal exists
   * only when the Less Traffic route
   * is active.
   *
   * It is placed around 55% along
   * the actual road route.
   */
  const trafficSignalPosition =
    traffic === 'Less Traffic' &&
    route &&
    route.length > 2
      ? route[
          Math.floor(
            route.length * 0.55
          )
        ]
      : null

  /*
   * Calculate approximate distance
   * between two latitude/longitude
   * positions in meters.
   */
  const calculateDistance = (
    position1,
    position2
  ) => {
    if (!position1 || !position2) {
      return Infinity
    }

    const earthRadius = 6371000

    const latitude1 =
      (position1[0] * Math.PI) / 180

    const latitude2 =
      (position2[0] * Math.PI) / 180

    const latitudeDifference =
      ((position2[0] -
        position1[0]) *
        Math.PI) /
      180

    const longitudeDifference =
      ((position2[1] -
        position1[1]) *
        Math.PI) /
      180

    const a =
      Math.sin(
        latitudeDifference / 2
      ) *
        Math.sin(
          latitudeDifference / 2
        ) +
      Math.cos(latitude1) *
        Math.cos(latitude2) *
        Math.sin(
          longitudeDifference / 2
        ) *
        Math.sin(
          longitudeDifference / 2
        )

    const c =
      2 *
      Math.atan2(
        Math.sqrt(a),
        Math.sqrt(1 - a)
      )

    return earthRadius * c
  }

  /*
   * Reset the emergency alert whenever
   * a new route animation starts.
   */
  useEffect(() => {
    setAlertShown(false)
  }, [routeVersion])

  /*
   * Automatically open the Traffic Signal
   * popup when the ambulance comes close
   * to the special node.
   */
  useEffect(() => {
    if (
      traffic !== 'Less Traffic' ||
      !trafficSignalPosition ||
      !ambulancePosition ||
      alertShown
    ) {
      return
    }

    const distanceToSignal =
      calculateDistance(
        ambulancePosition,
        trafficSignalPosition
      )

    /*
     * Alert distance:
     * approximately 60 meters.
     */
    if (distanceToSignal <= 60) {
      setAlertShown(true)

      if (
        trafficSignalRef.current
      ) {
        trafficSignalRef.current.openPopup()
      }
    }
  }, [
    ambulancePosition,
    traffic,
    trafficSignalPosition,
    alertShown,
  ])

  /*
   * Ambulance animation.
   */
  useEffect(() => {
    if (
      !routeStarted ||
      !route ||
      route.length < 2 ||
      routeVersion === 0
    ) {
      setAmbulancePosition(null)
      setHasArrived(false)
      return
    }

    let segmentIndex = 0
    let animationFrame = null
    let segmentStartTime = null
    let cancelled = false

    const totalAnimationTime = 15000

    const segmentDuration =
      totalAnimationTime /
      (route.length - 1)

    setAmbulancePosition(route[0])
    setHasArrived(false)

    const animate = (timestamp) => {
      if (cancelled) {
        return
      }

      if (segmentStartTime === null) {
        segmentStartTime = timestamp
      }

      const progress = Math.min(
        (timestamp - segmentStartTime) /
          segmentDuration,
        1
      )

      const start =
        route[segmentIndex]

      const end =
        route[segmentIndex + 1]

      const latitude =
        start[0] +
        (end[0] - start[0]) *
          progress

      const longitude =
        start[1] +
        (end[1] - start[1]) *
          progress

      setAmbulancePosition([
        latitude,
        longitude,
      ])

      if (progress < 1) {
        animationFrame =
          requestAnimationFrame(animate)

        return
      }

      segmentIndex += 1
      segmentStartTime = null

      if (
        segmentIndex <
        route.length - 1
      ) {
        animationFrame =
          requestAnimationFrame(animate)

        return
      }

      const destination =
        route[route.length - 1]

      setAmbulancePosition(
        destination
      )

      setHasArrived(true)

      animationFrame = null
    }

    animationFrame =
      requestAnimationFrame(animate)

    return () => {
      cancelled = true

      if (animationFrame !== null) {
        cancelAnimationFrame(
          animationFrame
        )
      }
    }
  }, [routeVersion])

  const destination =
    route && route.length > 0
      ? route[route.length - 1]
      : null

  const displayedAmbulancePosition =
    hasArrived &&
    ambulancePosition
      ? [
          ambulancePosition[0] +
            0.0002,
          ambulancePosition[1],
        ]
      : ambulancePosition

  return (
    <MapContainer
      center={[13.075, 80.258]}
      zoom={13}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <RouteViewport route={route} />

      {routeStarted &&
        route &&
        route.length > 1 && (
          <Polyline
            positions={route}
            pathOptions={{
              color: trafficColor,
              weight: 7,
              opacity: 0.9,
            }}
          />
        )}

      {/*
       * Traffic Signal node.
       *
       * This marker is rendered ONLY
       * for the Less Traffic route.
       */}
      {routeStarted &&
        traffic === 'Less Traffic' &&
        trafficSignalPosition && (
          <Marker
            ref={trafficSignalRef}
            position={
              trafficSignalPosition
            }
            icon={trafficSignalIcon}
            zIndexOffset={2000}
          >
            <Popup
              closeButton={true}
              autoClose={false}
            >
              <div
                style={{
                  minWidth: '260px',
                  lineHeight: '1.5',
                }}
              >
                <strong>
                  🚦 Traffic Signal
                </strong>

                <hr
                  style={{
                    margin:
                      '8px 0',
                  }}
                />

                <strong>
                  🚑 EMERGENCY ALERT
                </strong>

                <p
                  style={{
                    margin:
                      '6px 0',
                  }}
                >
                  Ambulance approaching
                  your junction.
                </p>

                <p
                  style={{
                    margin:
                      '6px 0',
                  }}
                >
                  <strong>
                    Traffic Police Action
                    Required:
                  </strong>{' '}
                  Clear and control traffic
                  to provide an unobstructed
                  passage for the ambulance.
                </p>

                <strong>
                  Priority: EMERGENCY VEHICLE
                </strong>
              </div>
            </Popup>
          </Marker>
        )}

      {/*
       * Highlight the Traffic Signal
       * node on the map.
       */}
      {routeStarted &&
        traffic === 'Less Traffic' &&
        trafficSignalPosition && (
          <CircleMarker
            center={
              trafficSignalPosition
            }
            radius={12}
            pathOptions={{
              color: 'orange',
              fillColor: 'yellow',
              fillOpacity: 0.35,
              weight: 3,
            }}
          />
        )}

      {Object.values(
        patientLocations
      ).map((patient) => {
        const isSelected =
          patient.id === selectedPatient

        return (
          <Marker
            key={patient.id}
            position={patient.position}
            icon={patientIcon}
            zIndexOffset={
              isSelected ? 1500 : 800
            }
          >
            <Popup>
              <strong>
                🏠 {patient.name}
              </strong>

              {isSelected && (
                <div>
                  Selected patient location
                </div>
              )}
            </Popup>
          </Marker>
        )
      })}

      {Object.values(hospitals).map(
        (hospital) => {
          const isSelected =
            hospital.id ===
            selectedHospital

          return (
            <Marker
              key={hospital.id}
              position={hospital.position}
              icon={hospitalIcon}
              zIndexOffset={
                isSelected ? 1500 : 1000
              }
            >
              <Popup>
                <strong>
                  🏥 {hospital.name}
                </strong>

                {isSelected && (
                  <div>
                    Selected destination
                  </div>
                )}
              </Popup>
            </Marker>
          )
        }
      )}

      {routeStarted &&
        selectedPatient &&
        patientLocations[
          selectedPatient
        ] && (
          <CircleMarker
            center={
              patientLocations[
                selectedPatient
              ].position
            }
            radius={7}
            pathOptions={{
              color: 'white',
              fillColor: 'green',
              fillOpacity: 1,
              weight: 2,
            }}
          />
        )}

      {routeStarted &&
        destination && (
          <CircleMarker
            center={destination}
            radius={7}
            pathOptions={{
              color: 'white',
              fillColor: 'red',
              fillOpacity: 1,
              weight: 2,
            }}
          />
        )}

      {routeStarted &&
        displayedAmbulancePosition && (
          <Marker
            position={
              displayedAmbulancePosition
            }
            icon={ambulanceIcon}
            zIndexOffset={2500}
          >
            <Popup>
              🚑 Ambulance

              {hasArrived && (
                <div>
                  Arrived at hospital
                </div>
              )}
            </Popup>
          </Marker>
        )}

      <div className="traffic-legend">
        <h3>🚦 Routes</h3>

        <div>
          <span className="legend-line less"></span>
          <span>Less Traffic</span>
        </div>

        <div>
          <span className="legend-line heavy"></span>
          <span>Heavy Traffic</span>
        </div>
      </div>
    </MapContainer>
  )
}

export default MapView
