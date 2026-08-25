"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Sparkles, 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Video, 
  Upload, 
  Mic, 
  Radio, 
  CheckCircle2, 
  FileText,
  UserCheck,
  RefreshCw,
  Sliders,
  Send,
  Zap
} from "lucide-react";

export function TalkingAvatarStudio() {
  const [scriptText, setScriptText] = useState(
    "Good morning Dalal Street! NIFTY 50 opens with strong institutional accumulation near 24,500. Reliance Industries and HDFC Bank show bullish momentum with PCR OI at 1.18. Hermes 3-Way Risk Committee recommends a 12% allocation into large-cap momentum breakouts with strict 2 ATR trailing stops."
  );
  const [selectedVoice, setSelectedVoice] = useState("en-IN-PrabhatNeural");
  const [avatarPreset, setAvatarPreset] = useState("ANCHOR_PRIYA");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [audioDuration, setAudioDuration] = useState(12);
  const [generatedResult, setGeneratedResult] = useState<any>(null);
  const [videoGenerated, setVideoGenerated] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const animationIntervalRef = useRef<any>(null);

  // Browser Speech Synthesis
  const speakWithBrowserSpeech = (text: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      const voices = window.speechSynthesis.getVoices();
      const indianVoice = voices.find(v => v.lang.includes("IN") || v.name.includes("India") || v.name.includes("Hindi"));
      if (indianVoice) utterance.voice = indianVoice;

      utterance.onstart = () => {
        setIsPlaying(true);
        startWaveformAnimation();
      };
      utterance.onend = () => {
        setIsPlaying(false);
        stopWaveformAnimation();
      };
      utterance.onerror = () => {
        setIsPlaying(false);
        stopWaveformAnimation();
      };

      window.speechSynthesis.speak(utterance);
    }
  };

  const startWaveformAnimation = () => {
    let elapsed = 0;
    const totalEst = Math.max(8, Math.round(scriptText.split(" ").length / 2.8));
    setAudioDuration(totalEst);
    
    if (animationIntervalRef.current) clearInterval(animationIntervalRef.current);
    animationIntervalRef.current = setInterval(() => {
      elapsed += 0.2;
      setAudioProgress(Math.min(100, (elapsed / totalEst) * 100));
      if (elapsed >= totalEst) {
        stopWaveformAnimation();
        setIsPlaying(false);
      }
    }, 200);
  };

  const stopWaveformAnimation = () => {
    if (animationIntervalRef.current) clearInterval(animationIntervalRef.current);
    setAudioProgress(0);
  };

  const handleSynthesizeAudio = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/voice/synthesize-briefing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: scriptText, voice: selectedVoice }),
      });
      const data = await res.json();
      setGeneratedResult(data);

      // Speak directly through speakers
      speakWithBrowserSpeech(scriptText);
    } catch (e) {
      console.error(e);
      speakWithBrowserSpeech(scriptText);
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (isPlaying) {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      setIsPlaying(false);
      stopWaveformAnimation();
    } else {
      speakWithBrowserSpeech(scriptText);
    }
  };

  const setPresetScript = (type: string) => {
    switch (type) {
      case "MORNING_BELL":
        setScriptText(
          "Dalal Street Opening Wrap: NIFTY 50 opens firm at 24,520 with positive global cues. FIIs turned net buyers with ₹840 Cr index futures accumulation. Focus on Banking and IT breakouts with 2 ATR trailing stops."
        );
        break;
      case "HERMES_TRADE":
        setScriptText(
          "Hermes Executive Alert: 4 Analysts and Dialectical Debate team have approved a high-conviction BUY on Reliance Industries at ₹2,969. Neutral Half-Kelly Arbiter assigns 12% capital allocation with stop loss at ₹2,865."
        );
        break;
      case "RISK_WARNING":
        setScriptText(
          "SEBI Risk & Volatility Advisory: India VIX expanded to 15.2 ahead of monthly expiry. Automated risk governors have scaled position sizing to 0.5x. Trailing stop losses tightened across all active F&O derivatives positions."
        );
        break;
    }
  };

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      stopWaveformAnimation();
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-950/70 via-[#0a0f1d]/90 to-indigo-950/70 border border-purple-500/30 rounded-2xl p-6 relative overflow-hidden backdrop-blur-xl shadow-2xl">
        <div className="absolute -right-10 -top-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-purple-400 font-mono text-xs uppercase tracking-widest">
              <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
              <span>Kokoro Neural Speech Synthesis & Live Talking Anchor Stage</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <span>Dalal Street AI Talking Avatar Studio</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono border border-purple-500/40">
                LIVE NEURAL TTS
              </span>
            </h1>
            <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Synthesize natural Indian English morning audio market briefs and generate animated talking presenter briefings for executive trading memos and daily Dalal Street opening wraps.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={togglePlayback}
              className={`px-5 py-3 rounded-xl font-bold font-mono text-xs flex items-center gap-2.5 shadow-lg transition ${
                isPlaying
                  ? "bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30 ring-1 ring-rose-400 animate-pulse"
                  : "bg-purple-600 hover:bg-purple-500 text-white shadow-purple-600/30 ring-1 ring-purple-400"
              }`}
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
              <span>{isPlaying ? "Stop Speaking" : "Play Live Briefing"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Avatar Presenter Stage & Teleprompter Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Live Speaking Avatar Presenter Visualizer */}
        <div className="lg:col-span-5 space-y-4">
          <div className="terminal-card p-6 flex flex-col items-center justify-center relative overflow-hidden bg-gradient-to-b from-[#0e1322] to-[#080c16] border-purple-500/40 shadow-2xl">
            {/* Live Presenter Stage */}
            <div className="relative w-48 h-48 md:w-56 md:h-56 rounded-full p-2 bg-gradient-to-b from-purple-500/40 via-cyan-500/20 to-transparent flex items-center justify-center my-4">
              {/* Outer Pulsing Rings */}
              {isPlaying && (
                <>
                  <div className="absolute inset-0 rounded-full border-2 border-purple-400/60 animate-ping" />
                  <div className="absolute -inset-3 rounded-full border border-cyan-400/40 animate-pulse" />
                </>
              )}

              {/* Avatar Face Container */}
              <div className="w-full h-full rounded-full bg-slate-900 overflow-hidden border-2 border-purple-400 flex flex-col items-center justify-center relative shadow-inner">
                {/* Presenter Portrait */}
                <div className="text-5xl select-none mb-1">👩‍💼</div>
                <div className="font-mono text-xs font-bold text-white tracking-wide">ANANYA SHARMA</div>
                <div className="text-[10px] font-mono text-purple-400">Chief Market Anchor</div>

                {/* Animated Speaking Waveform at Mouth Area */}
                {isPlaying ? (
                  <div className="flex items-center gap-1 mt-2 px-3 py-1 bg-purple-950/80 rounded-full border border-purple-500/50">
                    <span className="w-1 h-3 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1 h-5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    <span className="w-1 h-4 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: "100ms" }} />
                    <span className="w-1 h-3 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "250ms" }} />
                  </div>
                ) : (
                  <div className="flex items-center gap-1 mt-2 text-[10px] text-slate-500 font-mono">
                    <Volume2 className="w-3 h-3 text-slate-600" />
                    <span>READY TO SPEAK</span>
                  </div>
                )}
              </div>
            </div>

            {/* Speaking Status Pill */}
            <div className="flex items-center gap-2 font-mono text-xs">
              <span className={`w-2.5 h-2.5 rounded-full ${isPlaying ? "bg-emerald-400 animate-pulse shadow-glow-green" : "bg-slate-500"}`} />
              <span className={isPlaying ? "text-emerald-400 font-bold" : "text-slate-400"}>
                {isPlaying ? "BROADCASTING LIVE VOCAL BRIEFING" : "STUDIO IDLE • READY"}
              </span>
            </div>

            {/* Audio Waveform Spectrum Analyzer */}
            <div className="w-full mt-5 bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1.5 text-purple-400">
                  <Radio className="w-3.5 h-3.5" />
                  Neural Audio Stream
                </span>
                <span>{audioDuration}s Duration</span>
              </div>

              {/* Dynamic Frequency Bars */}
              <div className="flex items-end justify-between gap-1 h-10 px-1">
                {[40, 65, 85, 30, 95, 55, 75, 45, 90, 60, 80, 50, 70, 85, 35, 65, 90, 45, 80, 60].map((h, i) => (
                  <div
                    key={i}
                    className={`w-full rounded-t transition-all duration-150 ${
                      isPlaying ? "bg-gradient-to-t from-purple-600 to-cyan-400" : "bg-slate-800"
                    }`}
                    style={{
                      height: isPlaying ? `${Math.max(15, (h * Math.sin((i + audioProgress) * 0.5) + 50) % 100)}%` : "15%",
                    }}
                  />
                ))}
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mt-2">
                <div className="bg-gradient-to-r from-purple-500 to-cyan-400 h-1.5 rounded-full transition-all duration-200" style={{ width: `${audioProgress}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: Teleprompter Script Editor & Voice Controls */}
        <div className="lg:col-span-7 space-y-4">
          <div className="terminal-card p-6 space-y-4 font-mono text-xs">
            {/* Quick Preset Templates */}
            <div>
              <div className="text-slate-400 mb-2 flex items-center gap-1.5 font-bold">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span>TELEPROMPTER PRESET SCRIPTS</span>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setPresetScript("MORNING_BELL")}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition"
                >
                  Opening Bell Wrap
                </button>
                <button
                  onClick={() => setPresetScript("HERMES_TRADE")}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition"
                >
                  Hermes RIL Trade Alert
                </button>
                <button
                  onClick={() => setPresetScript("RISK_WARNING")}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition"
                >
                  SEBI Risk Caution
                </button>
              </div>
            </div>

            {/* Script Textarea */}
            <div>
              <label className="text-slate-400 block mb-1.5 font-bold">TELEPROMPTER SCRIPT (EDITABLE)</label>
              <textarea
                rows={5}
                value={scriptText}
                onChange={(e) => setScriptText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono leading-relaxed resize-none"
                placeholder="Enter script for the AI Avatar to speak..."
              />
            </div>

            {/* Voice & Accent Controls */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div>
                <label className="text-slate-400 block mb-1">NEURAL VOICE MODEL</label>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 text-xs text-white rounded-lg p-2 font-mono focus:outline-none focus:border-purple-500"
                >
                  <option value="en-IN-PrabhatNeural">Ananya (Indian English • Formal)</option>
                  <option value="en-IN-NeerjaNeural">Rahul (Indian English • Authoritative)</option>
                  <option value="en-IN-KokoroNeural">Kokoro-82M (Deep Dalal Street)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">BROADCAST ACCENT</label>
                <div className="p-2 bg-slate-900 border border-slate-800 rounded-lg text-purple-400 text-xs flex items-center justify-between">
                  <span>Indian English (Financial)</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                onClick={handleSynthesizeAudio}
                disabled={isGenerating}
                className="py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white rounded-xl font-bold font-mono text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 transition"
              >
                {isGenerating ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Synthesizing Speech...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Volume2 className="w-4 h-4" />
                    Synthesize & Speak Briefing
                  </span>
                )}
              </button>

              <button
                onClick={togglePlayback}
                className={`py-3 rounded-xl font-bold font-mono text-xs flex items-center justify-center gap-2 border transition ${
                  isPlaying
                    ? "bg-rose-500/20 text-rose-400 border-rose-500/40 hover:bg-rose-500/30"
                    : "bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800 hover:text-white"
                }`}
              >
                {isPlaying ? (
                  <>
                    <VolumeX className="w-4 h-4 text-rose-400" />
                    Stop Vocal Stream
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 text-emerald-400 fill-current" />
                    Live Voice Playback
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
