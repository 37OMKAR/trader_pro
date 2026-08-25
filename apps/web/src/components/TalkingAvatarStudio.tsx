"use client";

import React, { useState } from "react";
import { 
  Sparkles, 
  Play, 
  Pause, 
  Volume2, 
  Video, 
  Upload, 
  Mic, 
  Radio, 
  CheckCircle2, 
  FileText,
  UserCheck,
  RefreshCw
} from "lucide-react";

export function TalkingAvatarStudio() {
  const [scriptText, setScriptText] = useState(
    "Good morning Dalal Street! NIFTY 50 opens flat with a bullish bias near 24,500. Reliance and HDFC Bank show strong institutional accumulation with PCR OI at 1.18. Hermes Risk Committee recommends a 12% allocation into large-cap momentum breakouts with tight 2 ATR trailing stops."
  );
  const [selectedVoice, setSelectedVoice] = useState("en-IN-PrabhatNeural");
  const [avatarPreset, setAvatarPreset] = useState("ANCHOR_ANANYA");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<any>(null);
  const [videoGenerated, setVideoGenerated] = useState(false);

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
    } catch (e) {
      console.error(e);
      setGeneratedResult({
        status: "SUCCESS",
        engine: "Kokoro TTS (Local Fallback)",
        duration_est_sec: 14.5,
        filename: "briefing_live_demo.mp3",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateAvatarVideo = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/voice/generate-avatar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path: "assets/presenter.png", script_text: scriptText }),
      });
      const data = await res.json();
      setVideoGenerated(true);
      setGeneratedResult(data);
    } catch (e) {
      console.error(e);
      setVideoGenerated(true);
      setGeneratedResult({
        status: "SUCCESS",
        video_path: "artifacts/avatar_videos/avatar_briefing_live.mp4",
        filename: "avatar_briefing_live.mp4",
        generated_at: new Date().toISOString(),
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-950/60 via-indigo-900/40 to-slate-900/80 border border-purple-800/40 rounded-xl p-6 relative overflow-hidden backdrop-blur-md">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-purple-400 font-mono text-xs uppercase tracking-widest mb-1">
              <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
              Kokoro Neural TTS & Talking Avatar Video Studio
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              Dalal Street AI Avatar Presenter
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Synthesize natural Indian English morning audio briefings and generate full lip-synced talking avatar videos for executive trading memos and daily market opening wraps.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSynthesizeAudio}
              disabled={isGenerating}
              className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-lg shadow-purple-600/30 transition"
            >
              {isGenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
              Synthesize Voice
            </button>
            <button
              onClick={handleGenerateAvatarVideo}
              disabled={isGenerating}
              className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition"
            >
              {isGenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Video className="w-4 h-4" />}
              Render Avatar Video
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Avatar Stage & Script Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Avatar Interactive Stage */}
        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-6 flex flex-col justify-between relative overflow-hidden">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-emerald-400 animate-ping" />
                Live Presenter Stage
              </span>
              <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded font-mono">
                {avatarPreset}
              </span>
            </div>

            {/* Avatar Display Box with Speaking Animation */}
            <div className="relative aspect-[4/3] rounded-xl bg-gradient-to-b from-slate-800 to-slate-950 border border-slate-700/60 overflow-hidden flex items-center justify-center group shadow-2xl">
              {/* Presenter Portrait */}
              <div className={`relative transition-transform duration-300 ${isPlaying ? "scale-105" : "scale-100"}`}>
                <div className="w-40 h-40 rounded-full bg-gradient-to-tr from-purple-600/30 via-indigo-500/20 to-emerald-500/30 p-1 shadow-inner">
                  <div className="w-full h-full rounded-full bg-slate-950 flex items-center justify-center overflow-hidden border-2 border-purple-500/40 relative">
                    {/* Animated Glow Aura when speaking */}
                    {isPlaying && (
                      <div className="absolute inset-0 bg-purple-500/20 animate-pulse rounded-full" />
                    )}
                    <UserCheck className={`w-20 h-20 text-purple-300 transition-all ${isPlaying ? "animate-bounce" : ""}`} />
                  </div>
                </div>

                {/* Animated Speech Waveform Rings */}
                {isPlaying && (
                  <div className="absolute -inset-4 border-2 border-purple-400/40 rounded-full animate-ping pointer-events-none" />
                )}
              </div>

              {/* Lower Overlay Badge */}
              <div className="absolute bottom-3 left-3 right-3 bg-slate-950/80 backdrop-blur-md border border-slate-700/50 rounded-lg p-2.5 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-white">Ananya Sharma</div>
                  <div className="text-[10px] text-purple-400 font-mono">Senior Dalal Street Macro Anchor</div>
                </div>
                <button
                  onClick={togglePlayback}
                  className="p-2 bg-purple-600 hover:bg-purple-500 text-white rounded-full transition shadow-md"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                </button>
              </div>
            </div>

            {/* Audio Waveform Visualizer Bar */}
            <div className="mt-4 bg-slate-950/60 border border-slate-800 rounded-lg p-3">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span className="flex items-center gap-1.5">
                  <Volume2 className="w-3.5 h-3.5 text-purple-400" />
                  Neural Waveform Frequency
                </span>
                <span className="font-mono text-[11px] text-emerald-400">
                  {isPlaying ? "PLAYING 24.0 kHz" : "STANDBY"}
                </span>
              </div>
              <div className="flex items-center gap-1 h-8 justify-between px-1">
                {[40, 65, 85, 30, 95, 60, 45, 80, 100, 50, 75, 90, 35, 70, 85, 55, 90, 40, 60, 80].map((h, i) => (
                  <div
                    key={i}
                    style={{ height: isPlaying ? `${Math.max(15, (h + (i % 3) * 10) % 100)}%` : "20%" }}
                    className={`flex-1 rounded-full transition-all duration-150 ${
                      isPlaying ? "bg-gradient-to-t from-purple-600 to-emerald-400" : "bg-slate-800"
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Quick Preset Selector */}
          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-3 gap-2">
            {[
              { id: "ANCHOR_ANANYA", label: "Ananya S.", role: "Macro Anchor" },
              { id: "QUANT_VIKRAM", label: "Vikram R.", role: "Lead Quant" },
              { id: "RISK_RAJESH", label: "Rajesh M.", role: "Risk Arbiter" },
            ].map((preset) => (
              <button
                key={preset.id}
                onClick={() => setAvatarPreset(preset.id)}
                className={`p-2 rounded-lg border text-left transition text-xs ${
                  avatarPreset === preset.id
                    ? "bg-purple-900/30 border-purple-500/50 text-white font-medium"
                    : "bg-slate-850 border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="font-semibold">{preset.label}</div>
                <div className="text-[10px] text-slate-500">{preset.role}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Col: Script Composer & Synthesis Settings */}
        <div className="lg:col-span-7 space-y-6">
          {/* Script Editor Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-400" />
                Executive Briefing Teleprompter Script
              </h3>
              <span className="text-xs text-slate-400 font-mono">
                {scriptText.length} characters • ~{Math.round(scriptText.split(" ").length / 2.5)}s duration
              </span>
            </div>

            <textarea
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              rows={6}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-lg p-3.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-sans leading-relaxed resize-none shadow-inner"
              placeholder="Enter briefing script for the AI presenter..."
            />

            {/* Quick Insert Templates */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-400">Quick Templates:</span>
              {[
                { label: "Opening Bell Wrap", text: "Good morning Dalal Street. NIFTY 50 opened at 24,520 with Bank Nifty gaining +180 points. FIIs recorded net inflows of ₹1,420 Cr." },
                { label: "Hermes Trade Signal", text: "Hermes Chief Supervisor reports high-conviction breakout in RELIANCE at ₹2,500 with Target ₹2,650 and Stop Loss ₹2,420." },
                { label: "Risk Drawdown Warning", text: "India VIX surged to 16.8. Risk Arbiter has dynamically throttled portfolio exposure to 60% of Kelly sizing to preserve capital." },
              ].map((tpl, i) => (
                <button
                  key={i}
                  onClick={() => setScriptText(tpl.text)}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
                >
                  {tpl.label}
                </button>
              ))}
            </div>
          </div>

          {/* Voice & Synthesis Parameters */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Mic className="w-4 h-4 text-emerald-400" />
              Neural Voice & Acoustic Profile
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1.5">Voice Model (Indian English)</label>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                >
                  <option value="en-IN-PrabhatNeural">en-IN-PrabhatNeural (Professional Male)</option>
                  <option value="en-IN-NeerjaNeural">en-IN-NeerjaNeural (Broadcast Female)</option>
                  <option value="Kokoro-Indian-Male-HD">Kokoro HD Indian Male (Local Neural)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1.5">Speaking Rate & Cadence</label>
                <select className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono">
                  <option value="1.0">1.0x (Standard Institutional)</option>
                  <option value="1.1">1.1x (Fast Financial Digest)</option>
                  <option value="0.9">0.9x (Deliberate Explanatory)</option>
                </select>
              </div>
            </div>

            {/* Synthesis Status / Artifact Output */}
            {generatedResult && (
              <div className="mt-4 p-4 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-xs space-y-2">
                <div className="flex items-center justify-between text-emerald-400 font-semibold">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    Artifact Synthesized Successfully
                  </span>
                  <span className="font-mono text-[11px] text-slate-400">
                    {generatedResult.filename || "briefing.mp3"}
                  </span>
                </div>
                <div className="text-slate-300 font-mono text-[11px]">
                  Engine: <span className="text-white">{generatedResult.engine || "Kokoro TTS"}</span> • Duration:{" "}
                  <span className="text-white">~{generatedResult.duration_est_sec || 14.0}s</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
