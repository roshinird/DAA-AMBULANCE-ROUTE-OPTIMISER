import MapView from './components/MapView'
import RouteInfo from './components/RouteInfo'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>🚑 Ambulance Route Optimizer</h1>
          <p>Real-time traffic-aware emergency routing</p>
        </div>
      </header>

      <div className="map-container">
        <MapView />
      </div>

      <RouteInfo />
    </div>
  )
}

export default App
