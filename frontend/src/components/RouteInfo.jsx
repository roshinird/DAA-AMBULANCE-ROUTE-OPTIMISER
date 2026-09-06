import { useState } from 'react'
import { routeData } from '../data'

function RouteInfo() {
  const [routeStarted, setRouteStarted] = useState(false)
  const [rerouting, setRerouting] = useState(false)

  const handleStartRoute = () => {
    setRouteStarted(true)
  }

  const handleReroute = () => {
    setRerouting(true)

    setTimeout(() => {
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
        <strong>{routeData.eta}</strong>
      </div>

      <div className="info-item">
        <span>🚦 Traffic</span>
        <strong>{routeData.traffic}</strong>
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


