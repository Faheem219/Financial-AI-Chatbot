import React, { useState, useContext, useEffect } from "react";
import { getChatbotResponse, uploadPdf } from "../api/api";
import { AuthContext } from "../context/AuthContext";

const Chatbot = () => {
  const [prompt, setPrompt] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const { user } = useContext(AuthContext); // Get user info from context

  // Fetch chat history when the component mounts
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!user || !user.email) return; // Ensure user is available
      try {
        // Pass the user's email along with an empty prompt to fetch chat history
        const response = await getChatbotResponse(user.email, "");
        // The backend returns a list of arrays; if not, fallback to empty array.
        setChatHistory(response.history || []);
      } catch (err) {
        console.error("Failed to fetch chat history:", err);
      }
    };

    fetchChatHistory();
  }, [user]);

  const handlePromptSubmit = async (e) => {
    e.preventDefault();
    if (!prompt || !user || !user.email) return; // Ensure prompt and email are provided
    setLoading(true);
    try {
      // Pass the user's email and the prompt correctly to the API
      const response = await getChatbotResponse(user.email, prompt);
      // Append the new entry as an object with keys.
      setChatHistory([...chatHistory, { prompt, response: response.result }]);
      setPrompt("");
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handlePdfUpload = async (e) => {
    e.preventDefault();
    if (!pdfFile) return;
    try {
      await uploadPdf(pdfFile, ""); // Remove token if not needed here or pass correct token
      alert("PDF uploaded and processed successfully.");
      setPdfFile(null);
    } catch (err) {
      console.error(err);
      alert("PDF upload failed.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <header className="bg-white p-4 shadow mb-6">
        <h1 className="text-2xl font-bold">Financial Advisory Chatbot</h1>
      </header>
      <main className="container mx-auto">
        <div className="bg-white p-4 rounded shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Chat with our AI</h2>
          <div className="h-64 overflow-y-scroll p-2 border mb-4">
            {chatHistory.length === 0 ? (
              <p className="text-gray-500">No conversation yet.</p>
            ) : (
              chatHistory.map((chat, index) => {
                // Determine if chat is an array (from backend) or object (newly added)
                const promptText = Array.isArray(chat) ? chat[0] : chat.prompt;
                const responseText = Array.isArray(chat) ? chat[1] : chat.response;
                return (
                  <div key={index} className="mb-4">
                    <p>
                      <strong>You:</strong> {promptText}
                    </p>
                    <p>
                      <strong>AI:</strong> {responseText}
                    </p>
                  </div>
                );
              })
            )}
          </div>
          <form onSubmit={handlePromptSubmit} className="flex">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-grow p-2 border rounded-l"
              placeholder="Type your question..."
            />
            <button
              type="submit"
              className="bg-blue-500 text-white p-2 rounded-r hover:bg-blue-600"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">
            Upload Financial Statement (PDF)
          </h2>
          <form onSubmit={handlePdfUpload}>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setPdfFile(e.target.files[0])}
              className="mb-4"
            />
            <button
              type="submit"
              className="bg-green-500 text-white p-2 rounded hover:bg-green-600"
            >
              Upload PDF
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default Chatbot;
