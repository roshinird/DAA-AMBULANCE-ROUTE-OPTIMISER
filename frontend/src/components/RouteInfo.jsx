import { useState } from 'react'
import { routeData } from '../data'

function RouteInfo() {
  const [routeStarted, setRouteStarted] = useState(false)

  const handleStartRoute = () => {
    setRouteStarted(true)
  }

  const handleReroute = () => {
    alert('🔄 Rerouting...')
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
        <strong>{routeData.eta}</strong>
      </div>

      <div className="info-item">
        <span>🚦 Traffic</span>
        <strong>{routeData.traffic}</strong>
      </div>

      <div className="status">
        {routeStarted ? '🚑 Route Started' : `🟢 ${routeData.status}`}
      </div>

      <div className="route-buttons">
        <button onClick={handleStartRoute}>
          🚑 Start Route
        </button>

        <button onClick={handleReroute}>
          🔄 Reroute
        </button>
      </div>
    </div>
  )
}

export default RouteInfo


