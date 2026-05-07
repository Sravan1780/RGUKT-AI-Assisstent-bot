import React, { useState, useRef, useEffect } from "react";
import darkLogo from "./assets/darklogo.png";
import botIcon from "./assets/icon.png";
import { sendMessage } from "./services/api";
import {
  FaGraduationCap,
  FaAward,
  FaBuilding,
  FaCreditCard,
} from "react-icons/fa";

// ─── Card definitions ─────────────────────────────────────────────────────────
const CARDS = [
  {
    icon: <FaGraduationCap className="text-[#8BB9FE]" />,
    title: "Explore the",
    subtitle: "Eligibility Criteria",
    description: "for B.Tech Programs",
    borderColor: "border-blue-100",
    bgColor: "bg-blue-50",
    question: "What are the eligibility criteria and requirements for B.Tech programs at RGUKT?",
  },
  {
    icon: <FaAward className="text-[#98E9AB]" />,
    title: "Explore",
    subtitle: "Scholarship Options",
    description: "and Financial Aid",
    borderColor: "border-green-100",
    bgColor: "bg-green-50",
    question: "What scholarship options and financial aid are available for RGUKT students?",
  },
  {
    icon: <FaBuilding className="text-[#E5A0FF]" />,
    title: "Explore Campus",
    subtitle: "Recruitment",
    description: "Opportunities",
    borderColor: "border-pink-100",
    bgColor: "bg-pink-50",
    question: "Tell me about campus recruitment opportunities and placement services at RGUKT.",
  },
  {
    icon: <FaCreditCard className="text-[#FFE7A0]" />,
    title: "Learn About",
    subtitle: "Tuition Fees and",
    description: "Payment Methods",
    borderColor: "border-yellow-100",
    bgColor: "bg-yellow-50",
    question: "What are the tuition fees and available payment methods at RGUKT?",
  },
];

const COMMON_QUESTIONS = [
  "How do I apply for RGUKT admission?",
  "What documents are required for admission?",
  "What are the hostel facilities like?",
  "How can I prepare for campus placements?",
  "What B.Tech programs are offered?",
];

// ─── Typing indicator ─────────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3">
      <div className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center mr-2 flex-shrink-0">
        <img src={botIcon} alt="Bot" className="w-5 h-5 object-contain" />
      </div>
      <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-100">
        <div className="flex gap-1 items-center h-5">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Message bubble ────────────────────────────────────────────────────────────
function MessageBubble({ msg }) {
  const isUser = msg.type === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center mr-2 flex-shrink-0 mt-1">
          <img src={botIcon} alt="Bot" className="w-5 h-5 object-contain" />
        </div>
      )}
      <div
        className={`max-w-[85%] md:max-w-[78%] rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? "bg-gray-100 text-gray-800 rounded-tr-sm"
            : "bg-white border border-gray-100 text-gray-800 rounded-tl-sm"
        }`}
      >
        {isUser ? (
          <p className="text-sm md:text-base">{msg.text}</p>
        ) : (
          <div
            className="bot-response text-sm md:text-base"
            dangerouslySetInnerHTML={{ __html: msg.text }}
          />
        )}
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [serverHistory, setServerHistory] = useState([]);
  const [isChatting, setIsChatting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [error, setError] = useState("");

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isLoading]);

  // Focus input after bot replies
  useEffect(() => {
    if (!isLoading) inputRef.current?.focus();
  }, [isLoading]);

  const askQuestion = async (question) => {
    if (!question.trim() || isLoading) return;
    setError("");
    setIsChatting(true);

    // Optimistically add user message
    setChatHistory((prev) => [...prev, { type: "user", text: question }]);
    setMessage("");
    setIsLoading(true);

    try {
      const data = await sendMessage(question, serverHistory);
      setChatHistory((prev) => [...prev, { type: "bot", text: data.response }]);
      setServerHistory(data.chat_history || []);
    } catch (err) {
      const errMsg = err.message || "Something went wrong. Please try again.";
      setError(errMsg);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: `<p style="color:#ef4444">⚠️ ${errMsg}</p>` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(message);
  };

  const handleNewChat = () => {
    setChatHistory([]);
    setServerHistory([]);
    setMessage("");
    setIsChatting(false);
    setError("");
  };

  return (
    <div className="flex h-screen bg-white text-gray-900 overflow-hidden">
      {/* ── Sidebar toggle button ── */}
      <button
        onClick={() => setIsSidebarOpen((v) => !v)}
        className="fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
        aria-label="Toggle Sidebar"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* ── Sidebar ── */}
      <aside
        className={`fixed md:relative h-full bg-white border-r border-gray-100 z-40 transition-all duration-300 flex-shrink-0 ${
          isSidebarOpen ? "w-72 translate-x-0" : "w-0 -translate-x-full"
        } overflow-hidden`}
      >
        <div className="flex flex-col h-full p-5 pt-16">
          {/* Logo */}
          <div className="mb-6 flex justify-center">
            <img src={darkLogo} alt="RGUKT Logo" className="h-20 w-auto object-contain" />
          </div>

          {/* New Chat */}
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-4 py-2.5 mb-6 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>

          {/* Common Questions */}
          <div className="flex-1 overflow-y-auto">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Quick Questions
            </h2>
            <div className="space-y-1">
              {COMMON_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => askQuestion(q)}
                  disabled={isLoading}
                  className="text-left w-full text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Footer */}
          <p className="text-xs text-gray-400 text-center mt-4">
            RGUKT AI Assistant v2.0
          </p>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* ── Main content ── */}
      <main className="flex-1 flex flex-col min-w-0 h-full">
        {/* Landing / Hero area (only when no chat started) */}
        {!isChatting && (
          <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 pt-16">
            <div className="max-w-3xl mx-auto">
              {/* Logo */}
              <div className="flex justify-center mb-8">
                <img src={darkLogo} alt="RGUKT" className="h-24 md:h-32 w-auto" />
              </div>

              <h1 className="text-center text-2xl md:text-3xl font-semibold text-gray-800 mb-2">
                RGUKT AI Assistant
              </h1>
              <p className="text-center text-gray-500 mb-10 text-sm md:text-base">
                Ask me anything about Rajiv Gandhi University of Knowledge Technologies
              </p>

              {/* Clickable info cards — desktop */}
              <div className="hidden lg:grid grid-cols-4 gap-4 mb-10">
                {CARDS.map((card, i) => (
                  <button
                    key={i}
                    onClick={() => askQuestion(card.question)}
                    className={`p-5 rounded-2xl border ${card.borderColor} ${card.bgColor} hover:shadow-md hover:bg-white transition-all duration-200 flex flex-col items-center text-center`}
                  >
                    <span className="text-3xl mb-3">{card.icon}</span>
                    <span className="text-xs text-gray-500">{card.title}</span>
                    <span className="text-sm font-semibold text-gray-800">{card.subtitle}</span>
                    <span className="text-xs text-gray-500">{card.description}</span>
                  </button>
                ))}
              </div>

              {/* Mobile cards */}
              <div className="lg:hidden space-y-3 mb-8">
                {CARDS.map((card, i) => (
                  <button
                    key={i}
                    onClick={() => askQuestion(card.question)}
                    className={`w-full flex items-center gap-3 p-4 rounded-xl border ${card.borderColor} ${card.bgColor} hover:shadow-md hover:bg-white transition-all text-left`}
                  >
                    <span className="text-2xl flex-shrink-0">{card.icon}</span>
                    <span className="text-sm text-gray-700">{card.question}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chat messages */}
        {isChatting && (
          <div className="flex-1 overflow-y-auto px-4 md:px-8 py-4 pt-14">
            <div className="max-w-3xl mx-auto">
              {chatHistory.map((msg, i) => (
                <MessageBubble key={i} msg={msg} />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={chatEndRef} />
            </div>
          </div>
        )}

        {/* ── Input bar ── */}
        <div className="border-t border-gray-100 bg-white px-4 md:px-8 py-4">
          <form
            onSubmit={handleSubmit}
            className="max-w-3xl mx-auto flex items-center gap-2"
          >
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={isLoading}
                placeholder={isLoading ? "Thinking..." : "Ask me anything about RGUKT..."}
                className="w-full py-3 px-5 pr-12 rounded-full bg-gray-100 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base disabled:opacity-60"
              />
            </div>
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className="flex-shrink-0 w-11 h-11 rounded-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-200 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors shadow-sm"
              aria-label="Send"
            >
              {isLoading ? (
                <svg className="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                </svg>
              )}
            </button>
          </form>

          {error && (
            <p className="text-center text-xs text-red-500 mt-2">{error}</p>
          )}

          <p className="text-center text-xs text-gray-400 mt-2">
            RGUKT Assistant · Powered by Groq
          </p>
        </div>
      </main>
    </div>
  );
}
