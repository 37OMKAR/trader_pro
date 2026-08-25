"use client";

import React, { useState } from "react";
import { GraduationCap, Send, Sparkles, MessageCircle, ArrowRight } from "lucide-react";
import { MarketAPI } from "@/lib/api";

export function MarketTutorView() {
  const [question, setQuestion] = useState<string>("");
  const [messages, setMessages] = useState<any[]>([
    {
      role: "assistant",
      content: (
        "Namaste! I am your Dalal Street Market AI Tutor. " +
        "Ask me anything about Indian Equities, Black-Scholes Greeks, Option Chain Max Pain, " +
        "Market Regimes, STT taxation, or our Hermes Multi-Agent trading workflows."
      ),
    },
  ]);
  const [loading, setLoading] = useState<boolean>(false);

  const handleAsk = async (promptText?: string) => {
    const q = promptText || question;
    if (!q.trim() || loading) return;

    const userMsg = { role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await MarketAPI.askMarketTutor(q);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error communicating with AI Market Tutor. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "How does India VIX impact option premiums and Kelly position sizing?",
    "Explain Black-Scholes Delta, Gamma, Theta, and Vega for NSE Options.",
    "What is the difference between Weekly Thursday expiry and Monthly expiry?",
    "How does STT and regulatory slippage affect intraday strategy profitability?",
  ];

  return (
    <div className="space-y-6 font-mono text-xs max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="terminal-card p-5 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-bold text-white">DALAL STREET AI MARKET TUTOR</h2>
          </div>
          <div className="text-xs text-[#64748b] mt-0.5">
            Interactive Institutional Financial Mentor • Derivatives & Option Greeks • Market Regimes & Sizing Rules
          </div>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-2">
        {quickPrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => handleAsk(p)}
            className="px-3 py-1.5 rounded-full bg-[#0c1220] border border-[#1e293b] text-[#94a3b8] hover:text-white hover:border-purple-500/40 transition text-[10px]"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat Messages Window */}
      <div className="terminal-card p-5 space-y-4 min-h-[380px] max-h-[480px] overflow-y-auto bg-[#090d16]">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`p-3.5 rounded-lg max-w-[85%] leading-relaxed ${
                m.role === "user"
                  ? "bg-purple-600/20 border border-purple-500/40 text-white"
                  : "bg-[#0f172a] border border-[#1e293b] text-[#cbd5e1]"
              }`}
            >
              <div className="text-[10px] text-[#64748b] mb-1 font-bold">
                {m.role === "user" ? "YOU" : "DALAL STREET AI TUTOR"}
              </div>
              <div className="whitespace-pre-line text-[11px]">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-purple-400 text-xs animate-pulse">
            Dalal Street Tutor is synthesizing explanation...
          </div>
        )}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk();
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask anything about Indian markets, Greeks, strategy rules, or risk formulas..."
          className="flex-1 bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-white font-mono text-xs focus:outline-none focus:border-purple-500"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition flex items-center gap-1.5"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Ask Tutor</span>
        </button>
      </form>
    </div>
  );
}
