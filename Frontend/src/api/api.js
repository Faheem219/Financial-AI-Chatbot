// /src/api/api.js

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export async function loginUser({ email, password }) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }), // Send JSON with correct field names
    });
    if (!response.ok) {
        throw new Error('Login failed');
    }
    const data = await response.json();
    return data;
}

export async function signupUser({ email, username, password, income, expenses, investment_goals, risk_tolerance }) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, username, password, income, expenses, investment_goals, risk_tolerance }),
    });
    if (!response.ok) {
        throw new Error('Signup failed');
    }
    return response.json();
}

export async function getChatbotResponse(email, prompt) {
    const response = await fetch(`${API_BASE_URL}/chatbot/prompt`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, prompt }),
    });
    if (!response.ok) {
        throw new Error('Failed to get chatbot response');
    }
    return response.json();
}

export async function uploadPdf(file, email, token) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('email', email);  // Append the user's email

    const response = await fetch(`${API_BASE_URL}/chatbot/upload-pdf`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}`,
        },
        body: formData,
    });
    if (!response.ok) {
        throw new Error('Failed to upload PDF');
    }
    return response.json();
}

export async function getMarketData(symbol) {
    const response = await fetch(`${API_BASE_URL}/financial/market-data?symbol=${symbol}`);
    if (!response.ok) {
        throw new Error('Failed to fetch market data');
    }
    return response.json();
}

// NEW: Update user details
export async function updateUserDetails(income, expenses, investment_goals, risk_tolerance, token) {
    const response = await fetch(`${API_BASE_URL}/user/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            income,
            expenses,
            investment_goals,
            risk_tolerance,
        }),
    });
    if (!response.ok) {
        throw new Error('Failed to update user details');
    }
    return response.json();
}
