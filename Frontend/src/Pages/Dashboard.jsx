// /src/Pages/Dashboard.jsx
import React, { useContext, useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // Load the dark mode preference from localStorage, defaulting to false if not set.
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });

  // Whenever darkMode changes, update the HTML class and localStorage.
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Handle logout and redirect to login.
  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className={`min-h-screen p-4 transition-colors duration-300 ${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-black'}`}>
      {/* Header */}
      <header className={`flex justify-between items-center p-4 shadow mb-6 ${darkMode ? 'bg-gray-900' : 'bg-white'}`}>
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          {/* Dark Mode Toggle Button */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-3 py-1 border rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
        <div>
          {user && <span className="mr-4">Welcome, {user.username}</span>}
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      {/* main section */}
      <main className="container mx-auto">
        <h2 className="text-xl font-semibold mb-4">Your Financial Data</h2>
        <p>
          Here you can view your personalized financial information, investment insights, and more.
        </p>

        <div className="mt-6 flex space-x-4">
          <Link
            to="/chatbot"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Go to Chatbot
          </Link>

          {/* New link to edit details */}
          <Link
            to="/edit-details"
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
          >
            Edit Details
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
