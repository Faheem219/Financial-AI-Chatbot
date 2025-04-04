// /src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './Pages/Login';
import Signup from './Pages/Signup';
import Dashboard from './Pages/Dashboard';
import Chatbot from './Pages/Chatbot';
import Auth from './Pages/Auth';
import EditDetails from './Pages/EditDetails';
import Landingpage from './Pages/Landingpage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/auth/login" />} />
          <Route path="/auth" element={<Auth />}>
            <Route path="login" element={<Login />} />
            <Route path="signup" element={<Signup />} />
          </Route>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/edit-details" element={<EditDetails />} />
          <Route path="/landingpage" element={<Landingpage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
