import { useCallback, useState } from 'react'
import MapView from './components/MapView'
import RouteInfo from './components/RouteInfo'
import {
  patientLocations,
  hospitals,
} from './data'

const OSRM_BASE_URL =
  'https://router.project-osrm.org'

function App() {
  const [selectedPatient, setSelectedPatient] =
    useState('')

  const [selectedHospital, setSelectedHospital] =
    useState('')

  const [routeOptions, setRouteOptions] =
    useState({
      lessTraffic: null,
      heavyTraffic: null,
    })

  const [activeRoute, setActiveRoute] =
    useState('heavyTraffic')

  const [currentRoute, setCurrentRoute] =
    useState([])

  const [distance, setDistance] =
    useState('--')

  const [eta, setEta] =
    useState('--')

  const [traffic, setTraffic] =
    useState('Heavy Traffic')

  const [routeStarted, setRouteStarted] =
    useState(false)

  const [loadingRoutes, setLoadingRoutes] =
    useState(false)

  const [error, setError] =
    useState('')

  const [routeVersion, setRouteVersion] =
    useState(0)

  const resetRoute = useCallback(() => {
    setRouteStarted(false)

    setRouteOptions({
      lessTraffic: null,
      heavyTraffic: null,
    })

    setCurrentRoute([])

    setDistance('--')
    setEta('--')

    setTraffic('Heavy Traffic')
    setActiveRoute('heavyTraffic')

    setError('')
  }, [])

  const handlePatientChange = useCallback(
    (patientId) => {
      setSelectedPatient(patientId)
      resetRoute()
    },
    [resetRoute]
  )

  const handleHospitalChange = useCallback(
    (hospitalId) => {
      setSelectedHospital(hospitalId)
      resetRoute()
    },
    [resetRoute]
  )

  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${Math.round(meters)} m`
    }

    return `${(meters / 1000).toFixed(2)} km`
  }

  const formatEta = (seconds) => {
    const minutes = Math.max(
      1,
      Math.round(seconds / 60)
    )

    return `${minutes} min`
  }

  const convertRouteGeometry = (geometry) => {
    return geometry.coordinates.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    )
  }

  const createRouteData = (route) => {
    return {
      route: convertRouteGeometry(
        route.geometry
      ),
      distance: formatDistance(
        route.distance
      ),
      eta: formatEta(route.duration),
      durationSeconds: route.duration,
    }
  }

  const requestRoute = async (
    coordinates,
    extraOptions = ''
  ) => {
    const requestUrl =
      `${OSRM_BASE_URL}/route/v1/driving/` +
      coordinates +
      `?steps=false` +
      `&geometries=geojson` +
      `&overview=full` +
      extraOptions

    const response =
      await fetch(requestUrl)

    if (!response.ok) {
      throw new Error(
        'Unable to contact the routing service.'
      )
    }

    const data =
      await response.json()

    if (
      data.code !== 'Ok' ||
      !data.routes ||
      data.routes.length === 0
    ) {
      throw new Error(
        'Unable to calculate a road route.'
      )
    }

    return data.routes
  }

  const createFallbackWaypoint = (
    patient,
    hospital
  ) => {
    const [
      patientLatitude,
      patientLongitude,
    ] = patient.position

    const [
      hospitalLatitude,
      hospitalLongitude,
    ] = hospital.position

    const middleLatitude =
      (patientLatitude +
        hospitalLatitude) /
      2

    const middleLongitude =
      (patientLongitude +
        hospitalLongitude) /
      2

    const latitudeDifference =
      hospitalLatitude -
      patientLatitude

    const longitudeDifference =
      hospitalLongitude -
      patientLongitude

    const length = Math.sqrt(
      latitudeDifference *
        latitudeDifference +
        longitudeDifference *
        longitudeDifference
    )

    if (length === 0) {
      return [
        middleLatitude + 0.002,
        middleLongitude,
      ]
    }

    const offset = 0.0025

    const perpendicularLatitude =
      (-longitudeDifference /
        length) *
      offset

    const perpendicularLongitude =
      (latitudeDifference /
        length) *
      offset

    return [
      middleLatitude +
        perpendicularLatitude,
      middleLongitude +
        perpendicularLongitude,
    ]
  }

  const handleStartRoute = useCallback(
    async () => {
      if (
        !selectedPatient ||
        !selectedHospital
      ) {
        return
      }

      const patient =
        patientLocations[selectedPatient]

      const hospital =
        hospitals[selectedHospital]

      if (!patient || !hospital) {
        return
      }

      setLoadingRoutes(true)
      setError('')
      setRouteStarted(false)
      setCurrentRoute([])

      try {
        const [
          patientLatitude,
          patientLongitude,
        ] = patient.position

        const [
          hospitalLatitude,
          hospitalLongitude,
        ] = hospital.position

        const directCoordinates =
          `${patientLongitude},${patientLatitude};` +
          `${hospitalLongitude},${hospitalLatitude}`

        let routes =
          await requestRoute(
            directCoordinates,
            '&alternatives=true'
          )

        /*
         * OSRM may return only one route.
         * In that case, create a second
         * road-aligned route through a
         * nearby waypoint.
         */
        if (routes.length < 2) {
          const [
            waypointLatitude,
            waypointLongitude,
          ] = createFallbackWaypoint(
            patient,
            hospital
          )

          const fallbackCoordinates =
            `${patientLongitude},${patientLatitude};` +
            `${waypointLongitude},${waypointLatitude};` +
            `${hospitalLongitude},${hospitalLatitude}`

          const fallbackRoutes =
            await requestRoute(
              fallbackCoordinates
            )

          if (
            fallbackRoutes.length > 0
          ) {
            const firstRoute =
              routes[0]

            const secondRoute =
              fallbackRoutes[0]

            const firstPath =
              convertRouteGeometry(
                firstRoute.geometry
              )

            const secondPath =
              convertRouteGeometry(
                secondRoute.geometry
              )

            /*
             * Make sure the fallback is
             * actually different before
             * accepting it.
             */
            const firstMidpoint =
              firstPath[
                Math.floor(
                  firstPath.length / 2
                )
              ]

            const secondMidpoint =
              secondPath[
                Math.floor(
                  secondPath.length / 2
                )
              ]

            const midpointDifference =
              Math.abs(
                firstMidpoint[0] -
                  secondMidpoint[0]
              ) +
              Math.abs(
                firstMidpoint[1] -
                  secondMidpoint[1]
              )

            if (
              midpointDifference >
              0.0005
            ) {
              routes = [
                firstRoute,
                secondRoute,
              ]
            }
          }
        }

        if (
          !routes ||
          routes.length < 2
        ) {
          throw new Error(
            'Two distinct road routes could not be generated for this location pair. Please try another combination.'
          )
        }

        const firstRoute =
          createRouteData(routes[0])

        const secondRoute =
          createRouteData(routes[1])

        let lessTrafficRoute
        let heavyTrafficRoute

        if (
          firstRoute.durationSeconds <=
          secondRoute.durationSeconds
        ) {
          lessTrafficRoute = firstRoute
          heavyTrafficRoute = secondRoute
        } else {
          lessTrafficRoute = secondRoute
          heavyTrafficRoute = firstRoute
        }

        setRouteOptions({
          lessTraffic: lessTrafficRoute,
          heavyTraffic: heavyTrafficRoute,
        })

        /*
         * Heavy Traffic is always the
         * initial route.
         */
        setActiveRoute(
          'heavyTraffic'
        )

        setCurrentRoute(
          heavyTrafficRoute.route
        )

        setDistance(
          heavyTrafficRoute.distance
        )

        setEta(
          heavyTrafficRoute.eta
        )

        setTraffic(
          'Heavy Traffic'
        )

        setRouteStarted(true)

        setRouteVersion(
          (previousVersion) =>
            previousVersion + 1
        )
      } catch (routeError) {
        console.error(routeError)

        setError(
          routeError.message ||
            'Unable to calculate routes.'
        )

        setRouteStarted(false)
        setCurrentRoute([])
      } finally {
        setLoadingRoutes(false)
      }
    },
    [
      selectedPatient,
      selectedHospital,
    ]
  )

  const handleReroute = useCallback(() => {
    if (
      !routeStarted ||
      !routeOptions.lessTraffic ||
      !routeOptions.heavyTraffic
    ) {
      return
    }

    const nextRoute =
      activeRoute === 'heavyTraffic'
        ? 'lessTraffic'
        : 'heavyTraffic'

    const selectedRoute =
      routeOptions[nextRoute]

    setActiveRoute(nextRoute)

    setCurrentRoute(
      selectedRoute.route
    )

    setDistance(
      selectedRoute.distance
    )

    setEta(
      selectedRoute.eta
    )

    setTraffic(
      nextRoute === 'heavyTraffic'
        ? 'Heavy Traffic'
        : 'Less Traffic'
    )

    setRouteVersion(
      (previousVersion) =>
        previousVersion + 1
    )
  }, [
    activeRoute,
    routeOptions,
    routeStarted,
  ])

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>
            🚑 Ambulance Route Optimizer
          </h1>

          <p>
            Real-time traffic-aware emergency routing
          </p>
        </div>
      </header>

      <div className="map-container">
        <MapView
          route={currentRoute}
          traffic={traffic}
          selectedPatient={selectedPatient}
          selectedHospital={selectedHospital}
          routeStarted={routeStarted}
          routeVersion={routeVersion}
        />
      </div>

      <RouteInfo
        selectedPatient={selectedPatient}
        selectedHospital={selectedHospital}
        routeStarted={routeStarted}
        distance={distance}
        eta={eta}
        traffic={traffic}
        loadingRoutes={loadingRoutes}
        error={error}
        onPatientChange={handlePatientChange}
        onHospitalChange={handleHospitalChange}
        onStartRoute={handleStartRoute}
        onReroute={handleReroute}
      />
    </div>
  )
}

export default App
