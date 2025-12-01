"use client";

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError(null);
    setReply(null);

    try {
      const res = await fetch("http://localhost:8001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: { reply: string } = await res.json();
      setReply(data.reply);
    } catch (err: any) {
      setError(err.message || "Coś poszło nie tak");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100">
      <div className="w-full max-w-xl bg-slate-800 rounded-xl p-6 shadow-lg">
        <h1 className="text-2xl font-semibold mb-4 text-center">
          Virtual GF – chat MVP
        </h1>

        <label className="block mb-2 text-sm font-medium">
          Twoja wiadomość:
        </label>
        <textarea
          className="w-full rounded-md p-2 bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Napisz coś..."
        />

        <button
          onClick={handleSend}
          disabled={loading}
          className="mt-3 w-full py-2 rounded-md bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 font-medium"
        >
          {loading ? "Wysyłanie..." : "Wyślij"}
        </button>

        {error && <p className="mt-3 text-sm text-red-400">Błąd: {error}</p>}

        {reply && (
          <div className="mt-4 p-3 rounded-md bg-slate-900 border border-slate-700">
            <div className="text-xs text-slate-400 mb-1">Odpowiedź:</div>
            <div>{reply}</div>
          </div>
        )}
      </div>
    </main>
  );
}
