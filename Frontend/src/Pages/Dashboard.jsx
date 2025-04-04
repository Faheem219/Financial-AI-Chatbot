// /src/Pages/Dashboard.jsx
import React, { useContext, useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import Switch from './components/Switch';
import LogButton from './components/LogoutButton';

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // Load the dark mode preference from localStorage, defaulting to false if not set.
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });

  // Function to toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  };

  // Update the class on the document element based on darkMode state
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Handle logout and redirect to login
  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className={`min-h-screen p-6 transition-colors duration-300 ${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-black'}`}>
      {/* Header */}
      <header className={`flex justify-between items-center p-4 shadow mb-6 ${darkMode ? 'bg-gray-900' : 'bg-white'}`}>
        {/* Left Side */}
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold">Dashboard</h1>
        </div>

        {/* Center User Name */}
        <div className="flex-grow text-center">
          {user && <span className="mr-4 text-xl font-semibold">Welcome, {user.username} !!</span>}
        </div>

        {/* Right Side - Logout */}
        <div>
          <LogButton
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
          >
            Logout
          </LogButton>
        </div>
      </header>

      {/* Main Section */}
      <main className="container mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* User Details Card */}
        <div className={`p-6 shadow rounded-md ${darkMode ? 'bg-gray-700' : 'bg-white'}`}>
          <h3 className="font-semibold text-lg mb-4">Your Personal Details</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="font-medium"><strong>Income:</strong></p>
              <p className="text-gray-500">${user.income}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium"><strong>Expenses:</strong></p>
              <p className="text-gray-500">${user.expenses}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium"><strong>Investment Goals:</strong></p>
              <p className="text-gray-500">{user.investment_goals}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium"><strong>Risk Tolerance:</strong></p>
              <p className="text-gray-500">{user.risk_tolerance}</p>
            </div>
          </div>
          <div className="mt-8 text-center">
            <Link
              to="/edit-details"
              className="bg-green-500 text-white px-6 py-3 rounded hover:bg-green-600 transition-colors"
            >
              Edit Details
            </Link>
          </div>
        </div>

        {/* Chatbot Card */}
        <div className={`p-6 shadow rounded-md ${darkMode ? 'bg-gray-700' : 'bg-white'} flex flex-col justify-center items-center`}>
          <h3 className="font-semibold text-lg mb-4">Chatbot</h3>
          <p className="mb-6 text-center">
            Need personalized advice? Chat with our AI-powered chatbot to get financial insights, investment suggestions, and more!
          </p>
          <div className="flex-grow flex items-center justify-center">
            <Link
              to="/chatbot"
              className="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600 transition-colors"
            >
              Go to Chatbot
            </Link>
          </div>
        </div>

        {/* Any Additional Card for Future Use */}
        <div className={`p-6 shadow rounded-md ${darkMode ? 'bg-gray-700' : 'bg-white'}`}>
          <h3 className="font-semibold text-lg mb-4">Additional Section</h3>
          <p>This space can be used for any additional sections you want to add in the future.</p>
        </div>

      </main>

      {/* Dark Mode Toggle Button at Bottom */}
      <div className="absolute bottom-4 right-4 flex items-center">
        <span className="mr-2 font-semibold">Theme</span>
        <Switch isChecked={darkMode} onToggle={toggleDarkMode} />
      </div>
    </div>
  );
};

export default Dashboard;
