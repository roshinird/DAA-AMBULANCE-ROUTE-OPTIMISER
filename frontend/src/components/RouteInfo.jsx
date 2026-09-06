import { routeData } from '../data'

function RouteInfo() {
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
        🟢 {routeData.status}
      </div>
    </div>
  )
}

export default RouteInfo
