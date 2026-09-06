import { useCallback, useState } from 'react'
import MapView from './components/MapView'
import RouteInfo from './components/RouteInfo'
import { routeData } from './data'

const alternativeRoute = [
  [13.0827, 80.2707],
  [13.0795, 80.2670],
  [13.0760, 80.2600],
  [13.0715, 80.2520],
  [13.0685, 80.2440],
  [13.0674, 80.2376],
]

function App() {
  const [currentRoute, setCurrentRoute] = useState(routeData.route)
  const [traffic, setTraffic] = useState(routeData.traffic)
  const [eta, setEta] = useState(routeData.eta)
  const [rerouting, setRerouting] = useState(false)

  const handleTrafficChange = useCallback((newTraffic, newEta) => {
    setTraffic(newTraffic)
    setEta(newEta)

    if (newTraffic === 'Heavy') {
      setRerouting(true)

      setTimeout(() => {
        setCurrentRoute(alternativeRoute)
        setRerouting(false)
      }, 1000)
    }
  }, [])

  const handleReroute = useCallback(() => {
    setRerouting(true)

    setTimeout(() => {
      setCurrentRoute(alternativeRoute)
      setRerouting(false)
      alert('✅ New route calculated!')
    }, 1000)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>🚑 Ambulance Route Optimizer</h1>
          <p>Real-time traffic-aware emergency routing</p>
        </div>
      </header>

      <div className="map-container">
        <MapView route={currentRoute} />
      </div>

      <RouteInfo
        traffic={traffic}
        eta={eta}
        rerouting={rerouting}
        onTrafficChange={handleTrafficChange}
        onReroute={handleReroute}
      />
    </div>
  )
}

export default App
