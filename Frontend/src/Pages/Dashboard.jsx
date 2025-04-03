// /src/Pages/Dashboard.jsx
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <header className="flex justify-between items-center bg-white p-4 shadow mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div>
          {user && <span className="mr-4">Welcome, {user.username}</span>}
          <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">
            Logout
          </button>
        </div>
      </header>
      <main className="container mx-auto">
        <h2 className="text-xl font-semibold mb-4">Your Financial Data</h2>
        <p>Here you can view your personalized financial information, investment insights, and more.</p>
        <div className="mt-6">
          <Link to="/chatbot" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            Go to Chatbot
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
