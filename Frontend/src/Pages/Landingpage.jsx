// /src/Pages/Landing.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const Landing = () => {
    return (
        <div className="min-h-screen bg-white flex flex-col">
            {/* Hero Section */}
            <header className="relative w-full bg-gradient-to-r from-[rgb(127,96,219)] to-[#6e50c8] text-white">
                <div className="container mx-auto py-12 px-6 md:px-12 flex flex-col items-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4">
                        Welcome to FinSmart
                    </h1>
                    <p className="text-lg md:text-xl mb-6 text-center max-w-xl">
                        Your AI-powered financial advisor – helping you make smarter investment decisions and reach your financial goals.
                    </p>
                    <div className="flex space-x-3">
                        <Link
                            to="/auth/signup"
                            className="bg-white text-[rgb(127,96,219)] px-6 py-3 rounded shadow hover:bg-gray-50 font-semibold transition-colors"
                        >
                            Get Started
                        </Link>
                        <Link
                            to="/auth/login"
                            className="border border-white text-white px-6 py-3 rounded hover:bg-white hover:text-[rgb(127,96,219)] transition-colors font-semibold"
                        >
                            Login
                        </Link>
                    </div>
                </div>
            </header>

            {/* Features Section */}
            <main className="flex-grow container mx-auto px-6 md:px-12 py-12">
                <h2 className="text-3xl font-bold text-center mb-10 text-gray-800">
                    Why FinSmart?
                </h2>
                <div className="grid gap-8 md:grid-cols-3">
                    {/* Feature 1 */}
                    <div className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        <div className="mb-3 text-[rgb(127,96,219)]">
                            {/* Example icon */}
                            <svg
                                className="w-12 h-12 mx-auto"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path d="M12,0A12,12,0,1,0,24,12,12.01309,12.01309,0,0,0,12,0ZM7,11v2h4v5h2V13h4V11H13V6H11v5Z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2 text-center">
                            AI-Powered Insights
                        </h3>
                        <p className="text-gray-600 text-center">
                            Our chatbot uses cutting-edge AI to analyze market trends,
                            identify opportunities, and provide guidance tailored to your
                            financial profile.
                        </p>
                    </div>

                    {/* Feature 2 */}
                    <div className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        <div className="mb-3 text-[rgb(127,96,219)]">
                            <svg
                                className="w-12 h-12 mx-auto"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path d="M19,3H5A2.00229,2.00229,0,0,0,3,5V19a2.00229,2.00229,0,0,0,2,2H19a2.00229,2.00229,0,0,0,2-2V5A2.00229,2.00229,0,0,0,19,3Zm-8,14H7V7h4Zm6,0H13V7h4Z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2 text-center">
                            Personalized Dashboard
                        </h3>
                        <p className="text-gray-600 text-center">
                            Monitor your portfolio, track expenses, and view custom analytics
                            all in one place for a complete financial snapshot.
                        </p>
                    </div>

                    {/* Feature 3 */}
                    <div className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        <div className="mb-3 text-[rgb(127,96,219)]">
                            <svg
                                className="w-12 h-12 mx-auto"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path d="M21,11h-3a6,6,0,0,0-12,0H3a9,9,0,0,1,18,0Z" />
                                <path d="M12,13a3.00328,3.00328,0,0,0-3,3v5H9v2h6V21h0V16A3.00328,3.00328,0,0,0,12,13Zm1,7h-2V16a1,1,0,0,1,2,0Z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2 text-center">
                            Secure and Reliable
                        </h3>
                        <p className="text-gray-600 text-center">
                            Our platform uses advanced security measures to keep your
                            financial data safe and private.
                        </p>
                    </div>
                </div>
            </main>

            {/* Call to Action */}
            <section className="bg-[rgb(127,96,219)] py-12">
                <div className="container mx-auto px-6 md:px-12 text-center">
                    <h2 className="text-2xl md:text-3xl font-semibold text-white mb-4">
                        Ready to get started?
                    </h2>
                    <p className="text-white max-w-xl mx-auto mb-6">
                        Sign up now and take the first step toward a brighter financial
                        future.
                    </p>
                    <Link
                        to="/auth/signup"
                        className="bg-white text-[rgb(127,96,219)] px-8 py-3 rounded-md shadow hover:bg-gray-100 transition-colors font-semibold"
                    >
                        Create an Account
                    </Link>
                </div>
            </section>
        </div>
    );
};

export default Landing;
