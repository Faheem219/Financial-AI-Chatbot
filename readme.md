# 💬 AI-Powered Financial Advisory Chatbot 🚀💰

Welcome to the **AI-Powered Financial Advisory Chatbot** — your personalized guide to smarter investing and financial planning! 🌟  
This hackathon project is built to empower **young professionals in India** with intelligent insights, tailored strategies, and data-backed decisions. 🤖📊  

---

## 📚 Table of Contents
- [✨ Features](#-features)
- [🛠️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Usage](#-usage)

---

## ✨ Features

🔹 **Custom Investment Plans** based on your income, expenses, and risk profile.  
🔹 **Live Market Data** via Alpha Vantage + Historical Data from Kaggle.  
🔹 **Risk Profiling:** Tailored recommendations for **Low**, **Medium**, and **High** risk appetites.  
🔹 **Bank Statement Analysis:** Upload your PDF statements 📄 and receive actionable insights instantly.  
🔹 **LLM Magic:** Integrated with **Gemini API** for intelligent, context-aware conversations.  
🔹 **Modern UI:** Responsive and sleek interface using **React + TailwindCSS** ⚡  

---

## 🛠️ Tech Stack

| Layer        | Tech Used                                                                 |
|--------------|---------------------------------------------------------------------------|
| 🖼️ Frontend   | React (Vite), TailwindCSS                                                |
| ⚙️ Backend    | FastAPI                                                                  |
| 💾 Database   | MongoDB                                                                  |
| 🧠 LLM        | Google Gemini API via `google.generativeai`                              |
| 🧠 RAG        | Chroma Vector DB + LangChain + Torch                                     |
| 📊 Data Tools | Pandas, PyPDF2, Transformers                                             |

---

## 📁 Project Structure

```plaintext
.
├── frontend
│   ├── src
│   │   ├── api/api.js
│   │   ├── context/AuthContext.jsx
│   │   ├── Pages
│   │   │   ├── Auth.jsx
│   │   │   ├── Chatbot.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Signup.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
└── backend
    ├── api
    │   ├── auth.py
    │   ├── chatbot.py
    │   └── financial.py
    ├── core
    │   ├── config.py
    │   └── security.py
    ├── db
    │   ├── database.py
    │   └── mongo_setup.py
    ├── models
    │   ├── financial_info.py
    │   └── user.py
    ├── services
    │   ├── llm_service.py
    │   └── llm_gemini_service.py
    └── main.py
```

## 🚀 Usage Guide
1️⃣ Sign Up:
🔐 Create an account with your email, username, income, expenses, and goals.

2️⃣ Chatbot Interaction:
💬 Ask anything related to investing, savings, returns, and the chatbot will respond with insights based on real-time & historical market data.

3️⃣ Upload Bank Statements:
📤 Upload your PDF financial statements securely and receive personalized, AI-powered analysis.

### 🌱 Currently Ideal For
✅ Students and young professionals starting their investment journey

✅ Individuals looking for goal-based financial planning
