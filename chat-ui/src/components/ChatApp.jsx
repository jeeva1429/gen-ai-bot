import React, { useState } from "react";

export default function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🟢 Send query to backend
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    const formData = new FormData();
    formData.append("query", input);
    setMessages([...messages, userMessage]);
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/query/", {
        method: "POST",
        body: formData,
      });


      const data = await response.json();
      console.log(data)
      const botMessage = { sender: "bot", text: data.response || "No response" };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error connecting to server" },
      ])
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  // 🟣 Upload file handler
  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    const formData = new FormData();
    formData.append("file", uploadedFile);

    setMessages((prev) => [
      ...prev,
      { sender: "user", text: `📎 Uploaded: ${uploadedFile.name}` },
    ]);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.message || "File processed successfully!" },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ File upload failed." },
      ]);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg flex flex-col overflow-hidden">
        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 h-[70vh]">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-2 rounded-lg max-w-[75%] ${
                msg.sender === "user"
                  ? "bg-blue-500 text-white self-end ml-auto"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="text-gray-500 italic">Bot is thinking...</div>
          )}
        </div>

        {/* Input area */}
        <div className="flex items-center border-t p-3 gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something..."
            className="flex-1 p-2 border rounded-xl focus:outline-none"
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <input
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer bg-gray-200 px-3 py-2 rounded-xl hover:bg-gray-300"
          >
            📎
          </label>
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-4 py-2 rounded-xl hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
