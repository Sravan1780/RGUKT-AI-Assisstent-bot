const API_BASE = "https://rgukt-ai-assisstent-bot-production.up.railway.app/api";

/**
 * Send a chat message to the backend.
 * @param {string} text
 * @param {Array}  chatHistory
 * @returns {Promise<{response: string, timestamp: string, chat_history: Array}>}
 */
export async function sendMessage(text, chatHistory = []) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, chat_history: chatHistory }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }

  return res.json();
}

/**
 * Clear the backend chat history.
 */
export async function clearHistory() {
  const res = await fetch(`${API_BASE}/clear-history`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to clear history");
  return res.json();
}
