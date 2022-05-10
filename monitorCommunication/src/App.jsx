import './App.css'
import Monitor from './components/Monitor/monitor';
import WebSocketContext from "./context/socket";

function App() {
 
  return (
    <div className="App">
      <WebSocketContext>
          <Monitor/>
      </WebSocketContext>
    </div>
  )
}

export default App
