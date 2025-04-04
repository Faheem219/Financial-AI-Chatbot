// /src/Pages/EditDetails.jsx
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { updateUserDetails } from "../api/api";

const EditDetails = () => {
  const { user, token, login } = useContext(AuthContext);
  const navigate = useNavigate();

  // If no user is logged in, you might want to redirect them or show an error.
  if (!user) {
    // Optional: navigate('/auth/login');
    // or return some "Please login" message
  }

  const [income, setIncome] = useState(user ? user.income : 0);
  const [expenses, setExpenses] = useState(user ? user.expenses : 0);
  const [investmentGoals, setInvestmentGoals] = useState(
    user ? user.investment_goals : ""
  );
  const [riskTolerance, setRiskTolerance] = useState(
    user ? user.risk_tolerance : "medium"
  );
  const [error, setError] = useState(null);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const updatedUser = await updateUserDetails(
        parseFloat(income),
        parseFloat(expenses),
        investmentGoals,
        riskTolerance,
        token,
        user.email // pass the user's email here
      );

      // Update the AuthContext user with the updated data.
      login(updatedUser, token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form
        onSubmit={handleUpdate}
        className="max-w-md w-full bg-white p-8 shadow-md rounded"
      >
        <h2 className="text-2xl font-bold mb-6">Edit Your Details</h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <div className="mb-4">
          <label className="block text-gray-700">Income</label>
          <input
            type="number"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Expenses</label>
          <input
            type="number"
            value={expenses}
            onChange={(e) => setExpenses(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Investment Goals</label>
          <textarea
            value={investmentGoals}
            onChange={(e) => setInvestmentGoals(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Risk Tolerance</label>
          <select
            value={riskTolerance}
            onChange={(e) => setRiskTolerance(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
};

export default EditDetails;
