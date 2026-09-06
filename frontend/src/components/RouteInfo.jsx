import { useEffect, useState } from 'react'
import { routeData } from '../data'

function RouteInfo({ onReroute }) {
  const [routeStarted, setRouteStarted] = useState(false)
  const [rerouting, setRerouting] = useState(false)
  const [traffic, setTraffic] = useState(routeData.traffic)
  const [eta, setEta] = useState(routeData.eta)

  useEffect(() => {
    const trafficLevels = [
      { name: 'Low', eta: '10 min' },
      { name: 'Moderate', eta: '14 min' },
      { name: 'Heavy', eta: '20 min' },
    ]

    let index = 1

    const trafficTimer = setInterval(() => {
      const currentTraffic = trafficLevels[index]

      setTraffic(currentTraffic.name)
      setEta(currentTraffic.eta)

      index = (index + 1) % trafficLevels.length
    }, 5000)

    return () => clearInterval(trafficTimer)
  }, [])

  const handleStartRoute = () => {
    setRouteStarted(true)
  }

  const handleReroute = () => {
    setRerouting(true)

    setTimeout(() => {
      onReroute()
      setRerouting(false)
      alert('✅ New route calculated!')
    }, 1000)
  }

  return (
    <div className="route-info">
      <h2>🚑 Route Details</h2>

      <div className="info-item">
        <span>📍 Distance</span>
        <strong>{routeData.distance}</strong>
      </div>

      <div className="info-item">
        <span>⏱️ ETA</span>
        <strong>{eta}</strong>
      </div>

      <div className="info-item">
        <span>🚦 Traffic</span>
        <strong>{traffic}</strong>
      </div>

      <div className="status">
        {rerouting
          ? '🔄 Calculating new route...'
          : routeStarted
            ? '🚑 Route Started'
            : `🟢 ${routeData.status}`}
      </div>

      <div className="route-buttons">
        <button onClick={handleStartRoute}>
          🚑 Start Route
        </button>

        <button onClick={handleReroute} disabled={rerouting}>
          {rerouting ? '🔄 Rerouting...' : '🔄 Reroute'}
        </button>
      </div>
    </div>
  )
}

export default RouteInfo
