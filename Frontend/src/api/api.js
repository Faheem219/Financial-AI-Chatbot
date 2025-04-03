// /src/api/api.js
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export async function loginUser({ email, password }) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            username: email,
            password: password,
        }),
    });
    if (!response.ok) {
        throw new Error('Login failed');
    }
    return response.json();
}

export async function signupUser({ email, username, password }) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, username, password }),
    });
    if (!response.ok) {
        throw new Error('Signup failed');
    }
    return response.json();
}

export async function getChatbotResponse(prompt, token) {
    const response = await fetch(`${API_BASE_URL}/chatbot/prompt`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
        throw new Error('Failed to get chatbot response');
    }
    return response.json();
}

export async function uploadPdf(file, token) {
    const formData = new FormData();
    formData.append('file', file);
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
