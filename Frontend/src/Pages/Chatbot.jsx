// /src/Pages/Chatbot.jsx
import React, { useState, useContext, useEffect } from "react";
import { getChatbotResponse, uploadPdf } from "../api/api";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const Chatbot = () => {
  const [prompt, setPrompt] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const { user, token } = useContext(AuthContext);
  const navigate = useNavigate(); // For back button

  // --- CUSTOM PARSER FOR BOLD & LIST INDENTATION ---
  const parseChatText = (text) => {
    if (!text) return "";

    // Split text by newlines to process line-by-line
    const lines = text.split("\n");

    // Process each line for bold text and bullet/number indentation
    const processedLines = lines.map((line) => {
      // Convert **bold** to <strong>bold</strong>
      let replacedLine = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

      // Check if the line starts with digit+dot+space (e.g. "1. "),
      // or dash+space ("- "), or star+space ("* ").
      // If it does, we wrap it in a <div class="pl-4"> for indentation.
      if (/^\d+\.\s/.test(line) || /^-\s/.test(line) || /^\*\s/.test(line)) {
        replacedLine = `<div class="pl-4">${replacedLine}</div>`;
      } else {
        replacedLine = `<div>${replacedLine}</div>`;
      }
      return replacedLine;
    });

    // Join all processed lines into a single HTML string
    return processedLines.join("");
  };
  // ---------------------------------------------------

  // Fetch chat history when the component mounts
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!user || !user.email) return;
      try {
        const response = await getChatbotResponse(user.email, "");
        setChatHistory(response.history || []);
      } catch (err) {
        console.error("Failed to fetch chat history:", err);
      }
    };

    fetchChatHistory();
  }, [user]);

  const handlePromptSubmit = async (e) => {
    e.preventDefault();
    if (!prompt || !user || !user.email) return;
    setLoading(true);
    try {
      const response = await getChatbotResponse(user.email, prompt);
      setChatHistory([...chatHistory, { prompt, response: response.result }]);
      setPrompt("");
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handlePdfUpload = async (e) => {
    e.preventDefault();
    if (!pdfFile || !user || !user.email) return;
    try {
      await uploadPdf(pdfFile, user.email, token);
      alert("PDF uploaded and processed successfully.");
      setPdfFile(null);
    } catch (err) {
      console.error(err);
      alert("PDF upload failed.");
    }
  };

  const handleBackClick = () => {
    navigate(-1); // Go back to the previous page
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header with Back Button */}
      <header className="flex items-center justify-between mb-6">
        <button
          onClick={handleBackClick}
          className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
        >
          Back
        </button>
        <h1 className="text-3xl font-semibold text-center text-gray-800">
          Financial Advisory Chatbot
        </h1>
      </header>

      <main className="container mx-auto max-w-3xl bg-white p-6 rounded-lg shadow-lg">
        {/* Chatbot Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Chat with our AI
          </h2>
          <div className="max-h-[50vh] overflow-y-auto p-4 border rounded-lg bg-gray-50 shadow-inner space-y-4">
            {chatHistory.length === 0 ? (
              <p className="text-gray-500 text-center">No conversation yet.</p>
            ) : (
              chatHistory.map((chat, index) => {
                const promptText = Array.isArray(chat) ? chat[0] : chat.prompt;
                const responseText = Array.isArray(chat)
                  ? chat[1]
                  : chat.response;
                return (
                  <div key={index} className="mb-4">
                    {/* User's Message (Right Aligned) */}
                    <div className="flex justify-end mb-2">
                      <div
                        className="bg-blue-100 text-blue-800 p-3 rounded-lg max-w-[80%]"
                        dangerouslySetInnerHTML={{
                          __html: parseChatText(promptText),
                        }}
                      />
                    </div>
                    {/* AI's Response (Left Aligned) */}
                    <div className="flex justify-start mb-2">
                      <div
                        className="bg-green-100 text-green-800 p-3 rounded-lg max-w-[80%]"
                        dangerouslySetInnerHTML={{
                          __html: parseChatText(responseText),
                        }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Prompt Submission */}
          <form onSubmit={handlePromptSubmit} className="flex mt-4 space-x-2">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-grow p-3 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none overflow-hidden"
              placeholder="Type your question..."
              rows="1"
              onInput={(e) => {
                e.target.style.height = "auto";
                e.target.style.height = e.target.scrollHeight + "px";
              }}
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-3 rounded-md hover:bg-blue-600 disabled:bg-blue-300"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
        </div>

        {/* PDF Upload Section */}
        <div className="mt-6 bg-gray-100 p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Upload Financial Statement (PDF)
          </h2>
          <form onSubmit={handlePdfUpload} className="space-y-4">
            <div>
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setPdfFile(e.target.files[0])}
                className="block w-full text-sm text-gray-700 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-green-500 text-white py-3 rounded-md hover:bg-green-600"
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
