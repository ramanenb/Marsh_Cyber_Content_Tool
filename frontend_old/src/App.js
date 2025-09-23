import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import VizDashboard from './pages/Dashboard';
import SlideGeneration from './pages/SlideGeneration';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route exact path="/" element={<VizDashboard />} />
        <Route path="/dashboard" element={<VizDashboard />} />
        <Route path="/slidesCreationTool" element={<SlideGeneration />} />
        <Route path="*" element={<h2>You have entered a wrong url</h2>} />
      </Routes>
    </div>
  );
}

export default App;
