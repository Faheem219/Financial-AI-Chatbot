// /src/Pages/Dashboard.jsx
import React, { useContext, useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import Switch from "./components/Switch";
import LogButton from "./components/LogoutButton";
import logo from "./assets/logo.png"; // Import logo from assets

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // Load the dark mode preference from localStorage, defaulting to false if not set.
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });

  // Function to toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("theme", newMode ? "dark" : "light");
  };

  // Update the class on the document element based on darkMode state
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  // Handle logout and redirect to login
  const handleLogout = () => {
    logout();
    navigate("/auth/login");
  };

  return (
    <div
      className={`min-h-screen p-6 transition-colors duration-300 ${
        darkMode ? "bg-gray-800 text-white" : "bg-gray-100 text-black"
      }`}
    >
      {/* Header */}
      <header
        className={`flex justify-between items-center p-4 shadow-md rounded-lg mb-6 ${
          darkMode ? "bg-gray-900" : "bg-white"
        }`}
      >
        {/* Left Side - Logo */}
        <div className="flex items-center space-x-4">
          <img src={logo} alt="Logo" className="h-12 w-auto" />{" "}
          {/* Logo added here */}
          <h1 className="text-3xl font-semibold">Dashboard</h1>
        </div>

        {/* Center User Name */}
        <div className="flex-grow text-center">
          {user && (
            <span className="text-xl font-semibold">
              Welcome, {user.username}!
            </span>
          )}
        </div>

        {/* Right Side - Logout */}
        <div>
          <LogButton
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors"
          >
            Logout
          </LogButton>
        </div>
      </header>

      {/* Main Section */}
      <main className="container mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 justify">
        {/* User Details Card */}
        <div
          className={`p-6 shadow-lg rounded-xl ${
            darkMode ? "bg-gray-700" : "bg-white"
          } transition-shadow duration-300`}
        >
          <h3 className="font-semibold text-lg mb-4">Your Personal Details</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="font-medium">
                <strong>Income:</strong>
              </p>
              <p className="text-gray-500">₹{user.income}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium">
                <strong>Expenses:</strong>
              </p>
              <p className="text-gray-500">₹{user.expenses}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium">
                <strong>Investment Goals:</strong>
              </p>
              <p className="text-gray-500">{user.investment_goals}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="font-medium">
                <strong>Risk Tolerance:</strong>
              </p>
              <p className="text-gray-500">{user.risk_tolerance}</p>
            </div>
          </div>
          <div className="mt-8 text-center">
            <Link
              to="/edit-details"
              className="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 transition-colors"
            >
              Edit Details
            </Link>
          </div>
        </div>

        {/* Chatbot Card */}
        <div
          className={`p-6 shadow-lg rounded-xl ${
            darkMode ? "bg-gray-700" : "bg-white"
          } flex flex-col justify-center items-center transition-shadow duration-300`}
        >
          <h3 className="font-semibold text-lg mb-4">Chatbot</h3>
          <p className="mb-6 text-center">
            Need personalized advice? Chat with our AI-powered chatbot to get
            financial insights, investment suggestions, and more!
          </p>
          <div className="flex-grow flex items-center justify-center">
            <Link
              to="/chatbot"
              className="bg-[rgb(127,96,219)] text-white px-6 py-3 rounded-md hover:bg-[rgb(112,75,185)] transition-colors"
            >
              Go to Chatbot
            </Link>
          </div>
        </div>
        <div
          className={`p-6 shadow-lg rounded-xl ${
            darkMode ? "bg-gray-700" : "bg-white"
          } flex flex-col justify-center items-center transition-shadow duration-300`}
        >
          <h3 className="font-semibold text-lg mb-4">Stay tuned!!</h3>
          <p className="mb-6 text-center">
            Stay tuned for more features and updates coming soon! We are
            constantly working to enhance your experience and provide you with
            the best financial advisory services.
          </p>
          <div className="flex-grow flex items-center justify-center"></div>
        </div>
      </main>

      {/* LLM and Dataset Information Cards (Horizontal Layout) */}
      <section className="container mx-auto mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
        {/* About Our LLM Model Card */}
        <div
          className={`p-6 shadow-lg rounded-xl ${
            darkMode ? "bg-gray-700" : "bg-white"
          } transition-shadow duration-300`}
        >
          <h3 className="font-semibold text-lg mb-4">About Our LLM Model</h3>
          <p className="text-gray-500 mb-4">
            Our Language Learning Model (LLM) is powered by state-of-the-art AI
            technology, designed to assist you with personalized financial
            planning, insights, and risk assessments.
          </p>
          <p className="text-gray-500 mb-4">Key Features:</p>
          <ul className="list-disc pl-5 text-gray-500">
            <li>Generates personalized financial plans based on user data.</li>
            <li>
              Provides real-time market insights and investment suggestions.
            </li>
            <li>
              Performs risk analysis based on financial conditions and goals.
            </li>
            <li>
              Integrates seamlessly with your personal data for highly accurate
              results.
            </li>
          </ul>
          <p className="text-gray-500 mt-4">
            Our model uses advanced language understanding to provide answers to
            complex financial queries, making it an indispensable tool for any
            user looking to manage their finances effectively.
          </p>
        </div>

        {/* About the Dataset Card */}
        <div
          className={`p-6 shadow-lg rounded-xl ${
            darkMode ? "bg-gray-700" : "bg-white"
          } transition-shadow duration-300`}
        >
          <h3 className="font-semibold text-lg mb-4">About the Dataset</h3>
          <p className="text-gray-500 mb-4">
            The LLM is trained on a diverse and extensive dataset sourced from
            various financial domains, including:
          </p>
          <ul className="list-disc pl-5 text-gray-500 mb-4">
            <li>Historical stock data from global exchanges.</li>
            <li>Company earnings reports and financial statements.</li>
            <li>Market analysis and financial research papers.</li>
            <li>Financial advisory content and investment strategies.</li>
          </ul>
          <p className="text-gray-500">
            This comprehensive dataset enables the model to provide highly
            accurate, data-driven financial insights, predictions, and
            recommendations tailored to each user's financial situation.
          </p>
        </div>
      </section>

      {/* Dark Mode Toggle Button at Bottom */}
      <div className="absolute bottom-6 right-6 flex items-center">
        <span className="mr-2 font-semibold">Theme</span>
        <Switch isChecked={darkMode} onToggle={toggleDarkMode} />
      </div>
    </div>
  );
};

export default Dashboard;
