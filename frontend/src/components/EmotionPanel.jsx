import React from 'react';
import { Smile, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';

export function EmotionPanel({ data }) {
  const dominant = data?.dominant_emotion || 'Neutral';
  const confidence = Math.round((data?.confidence || 0) * 100);
  const distribution = data?.distribution || {
    Neutral: 0.90, Happy: 0.03, Sad: 0.02, Surprise: 0.02, Fear: 0.01, Disgust: 0.01, Angry: 0.01
  };
  // New: sustained events from the 3s gate — array of factual strings
  const sustainedEvents = data?.sustained_events || [];
  const observationLabel = data?.observation_label || null;

  const getEmotionColor = (emotion) => {
    switch (emotion) {
      case 'Happy':   return 'bg-emerald-500';
      case 'Sad':     return 'bg-blue-500';
      case 'Fear':    return 'bg-purple-500';
      case 'Angry':   return 'bg-rose-500';
      case 'Disgust': return 'bg-amber-600';
      case 'Surprise':return 'bg-yellow-400';
      default:        return 'bg-cyan-500';
    }
  };

  // Badge colour for dominant emotion chip
  const getDominantBadgeColor = (emotion) => {
    const map = {
      Happy: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
      Sad: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
      Fear: 'text-purple-300 bg-purple-500/10 border-purple-500/30',
      Angry: 'text-rose-300 bg-rose-500/10 border-rose-500/30',
      Disgust: 'text-amber-300 bg-amber-600/10 border-amber-600/30',
      Surprise: 'text-yellow-300 bg-yellow-400/10 border-yellow-500/30',
    };
    return map[emotion] || 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30';
  };

  const STRESS_EMOTIONS = ['Sad', 'Fear', 'Disgust', 'Angry'];
  const isDominantStress = STRESS_EMOTIONS.includes(dominant);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Smile className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Emotion Tracker</h3>
            <p className="text-[11px] text-slate-400">ViT-Base AffectNet+ · 30-frame avg</p>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border block mb-0.5 ${getDominantBadgeColor(dominant)}`}>
            {dominant}
          </span>
          <span className="text-[10px] text-slate-400">{confidence}% conf</span>
        </div>
      </div>

      {/* Sustained Expression Log — replaces "Clinical Stress Score" */}
      <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
        <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
          <Clock className="w-3 h-3" />
          Sustained Expression Log
        </div>

        {sustainedEvents.length > 0 ? (
          <div className="space-y-1.5 max-h-20 overflow-y-auto">
            {sustainedEvents.map((evt, i) => (
              <div
                key={i}
                className="flex items-center gap-2 bg-amber-950/40 border border-amber-800/50 px-2.5 py-1.5 rounded-lg text-[11px] text-amber-200"
              >
                <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                <span>{evt}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-[11px] text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            {isDominantStress
              ? <span className="text-slate-400">Monitoring — threshold not yet reached (3s required)</span>
              : <span>No sustained non-neutral expression detected.</span>
            }
          </div>
        )}

        {/* Subtle hint when a non-neutral emotion is building up */}
        {isDominantStress && sustainedEvents.length === 0 && (
          <div className="mt-2 w-full h-1 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500/60 to-amber-400/40 rounded-full animate-pulse"
              style={{ width: '40%' }}
            />
          </div>
        )}
      </div>

      {/* 7-Emotion Probability Distribution Bars (raw data — kept as-is) */}
      <div className="space-y-2">
        {Object.entries(distribution).map(([emotion, prob]) => {
          const pct = Math.round((prob || 0) * 100);
          return (
            <div key={emotion} className="flex items-center gap-2 text-xs">
              <span className="w-16 text-[11px] text-slate-400 truncate">{emotion}</span>
              <div className="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${getEmotionColor(emotion)}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="w-8 text-[10px] font-mono text-slate-400 text-right">{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

