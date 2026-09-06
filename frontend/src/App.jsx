import MapView from './components/MapView'
import RouteInfo from './components/RouteInfo'

function App() {
  return (
    <div className="app">
      <div className="map-container">
        <MapView />
      </div>

      <RouteInfo />
    </div>
  )
}

export default App
