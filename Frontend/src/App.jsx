import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import { AuthProvider } from './context/AuthContext';
// import { ThemeProvider } from './context/ThemeContext';
// import Auth from './components/Auth';
import Dashboard from './Pages/Dashboard';
import ChatBot from './Pages/Chatbot';
import Signup from './Pages/Signup';
import Login from './Pages/Login';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router>
          <Routes>
            <Route path='/dashboard' element={<Dashboard/>} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;