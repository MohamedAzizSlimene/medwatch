import React from 'react';
import { Smile, Brain } from 'lucide-react';

export function EmotionPanel({ data }) {
  const dominant = data?.dominant_emotion || 'Neutral';
  const confidence = Math.round((data?.confidence || 0) * 100);
  const stressScore = Math.round((data?.clinical_stress_score || 0) * 100);
  const distribution = data?.distribution || {
    Neutral: 0.90, Happy: 0.03, Sad: 0.02, Surprise: 0.02, Fear: 0.01, Disgust: 0.01, Angry: 0.01
  };

  const getEmotionColor = (emotion) => {
    switch (emotion) {
      case 'Happy': return 'bg-emerald-500';
      case 'Sad': return 'bg-blue-500';
      case 'Fear': return 'bg-purple-500';
      case 'Angry': return 'bg-rose-500';
      case 'Disgust': return 'bg-amber-600';
      case 'Surprise': return 'bg-yellow-400';
      default: return 'bg-cyan-500';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Smile className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Emotion & Stress</h3>
            <p className="text-[11px] text-slate-400">ViT-Base AffectNet+ Soft Labels</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-cyan-400 block">{dominant}</span>
          <span className="text-[10px] text-slate-400">{confidence}% conf</span>
        </div>
      </div>

      {/* Clinical Stress Score Gauge */}
      <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Brain className="w-3.5 h-3.5 text-cyan-400" />
            Clinical Stress Score
          </span>
          <span className={`font-bold ${stressScore > 50 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {stressScore}%
          </span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              stressScore > 60 ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-gradient-to-r from-cyan-500 to-emerald-400'
            }`}
            style={{ width: `${stressScore}%` }}
          />
        </div>
      </div>

      {/* 7-Emotion Probability Distribution Bars */}
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
