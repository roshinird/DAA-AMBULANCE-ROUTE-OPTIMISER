function RouteInfo() {
  return (
    <div className="route-info">
      <h2>🚑 Ambulance Route</h2>

      <div className="info-item">
        <strong>Distance</strong>
        <span>6.8 km</span>
      </div>

      <div className="info-item">
        <strong>ETA</strong>
        <span>14 min</span>
      </div>

      <div className="info-item">
        <strong>Traffic</strong>
        <span>Moderate</span>
      </div>

      <div className="status">
        🟢 Route Active
      </div>
    </div>
  )
}

export default RouteInfo
