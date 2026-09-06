import { routeData } from '../data'

function RouteInfo() {
  return (
    <div className="route-info">
      <h2>🚑 Ambulance Route</h2>

      <div className="info-item">
        <strong>Distance</strong>
        <span>{routeData.distance}</span>
      </div>

      <div className="info-item">
        <strong>ETA</strong>
        <span>{routeData.eta}</span>
      </div>

      <div className="info-item">
        <strong>Traffic</strong>
        <span>{routeData.traffic}</span>
      </div>

      <div className="status">
        🟢 {routeData.status}
      </div>
    </div>
  )
}

export default RouteInfo
