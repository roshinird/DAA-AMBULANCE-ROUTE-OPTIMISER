import { useEffect, useState } from 'react'
import { routeData } from '../data'

function RouteInfo({
  traffic,
  eta,
  rerouting,
  onTrafficChange,
  onReroute,
}) {
  const [routeStarted, setRouteStarted] = useState(false)

  useEffect(() => {
    const trafficLevels = [
      { name: 'Low', eta: '10 min' },
      { name: 'Moderate', eta: '14 min' },
      { name: 'Heavy', eta: '20 min' },
    ]

    let index = 1

    const trafficTimer = setInterval(() => {
      const currentTraffic = trafficLevels[index]

      onTrafficChange(currentTraffic.name, currentTraffic.eta)

      index = (index + 1) % trafficLevels.length
    }, 5000)

    return () => clearInterval(trafficTimer)
  }, [onTrafficChange])

  const handleStartRoute = () => {
    setRouteStarted(true)
  }

  const handleReroute = () => {
    onReroute()
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
