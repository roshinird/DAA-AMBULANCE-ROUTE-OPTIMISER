import { patientLocations, hospitals } from '../data'

function RouteInfo({
  selectedPatient,
  selectedHospital,
  routeStarted,
  distance,
  eta,
  traffic,
  loadingRoutes,
  error,
  onPatientChange,
  onHospitalChange,
  onStartRoute,
  onReroute,
}) {
  const handleStartRoute = () => {
    if (
      !selectedPatient ||
      !selectedHospital ||
      loadingRoutes
    ) {
      return
    }

    onStartRoute()
  }

  const handleReroute = () => {
    if (
      !routeStarted ||
      loadingRoutes
    ) {
      return
    }

    onReroute()
  }

  const isHeavyTraffic =
    traffic === 'Heavy Traffic'

  return (
    <div className="route-info">
      <h2>🚑 Route Details</h2>

      <div className="selection-group">
        <label htmlFor="patient-select">
          🏠 Patient Location
        </label>

        <select
          id="patient-select"
          value={selectedPatient}
          onChange={(event) =>
            onPatientChange(
              event.target.value
            )
          }
          disabled={loadingRoutes}
        >
          <option value="">
            Select Patient Home
          </option>

          {Object.values(
            patientLocations
          ).map((patient) => (
            <option
              key={patient.id}
              value={patient.id}
            >
              {patient.name}
            </option>
          ))}
        </select>
      </div>

      <div className="selection-group">
        <label htmlFor="hospital-select">
          🏥 Destination Hospital
        </label>

        <select
          id="hospital-select"
          value={selectedHospital}
          onChange={(event) =>
            onHospitalChange(
              event.target.value
            )
          }
          disabled={loadingRoutes}
        >
          <option value="">
            Select Hospital
          </option>

          {Object.values(
            hospitals
          ).map((hospital) => (
            <option
              key={hospital.id}
              value={hospital.id}
            >
              {hospital.name}
            </option>
          ))}
        </select>
      </div>

      <div className="info-item">
        <span>📍 Distance</span>
        <strong>{distance}</strong>
      </div>

      <div className="info-item">
        <span>⏱️ ETA</span>
        <strong>{eta}</strong>
      </div>

      <div className="info-item">
        <span>🚦 Traffic</span>

        <strong
          className={
            isHeavyTraffic
              ? 'traffic-heavy'
              : 'traffic-less'
          }
        >
          {traffic}
        </strong>
      </div>

      {loadingRoutes && (
        <div className="loading-message">
          🗺️ Finding two road routes...
        </div>
      )}

      {error && (
        <div className="route-error">
          ⚠️ {error}
        </div>
      )}

      <div
        className={`status ${
          isHeavyTraffic
            ? 'status-heavy'
            : ''
        }`}
      >
        {routeStarted
          ? isHeavyTraffic
            ? '🔴 Heavy Traffic Route Active'
            : '🟢 Less Traffic Route Active'
          : '📍 Select locations and start the route'}
      </div>

      <div className="route-buttons">
        <button
          className="start-route-button"
          onClick={handleStartRoute}
          disabled={
            !selectedPatient ||
            !selectedHospital ||
            loadingRoutes
          }
        >
          {loadingRoutes
            ? '⏳ Finding Routes...'
            : '🚑 Start Route'}
        </button>

        <button
          className="reroute-button"
          onClick={handleReroute}
          disabled={
            !routeStarted ||
            loadingRoutes
          }
        >
          🔄 Reroute
        </button>
      </div>
    </div>
  )
}

export default RouteInfo
