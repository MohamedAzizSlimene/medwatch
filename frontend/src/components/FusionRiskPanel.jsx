import React from 'react';
import { Activity, AlertCircle, CheckCircle2, Wind, Smile, Clock } from 'lucide-react';

export function FusionRiskPanel({ data }) {
  const sessionStatus = data?.session_status || 'BASELINE NORMAL';
  const telemetry = data?.telemetry || {
    coughs: 0,
    sneezes: 0,
    hand_gestures: 0,
    stress_score_pct: 0,
    dominant_emotion: 'Neutral',
    yawn_count: 0,
    fatigue_status: 'NORMAL'
  };
  const observations = data?.active_observations || data?.active_alerts || [];

  const getStatusBadge = () => {
    switch (sessionStatus) {
      case 'ELEVATED ACTIVITY':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold animate-pulse';
      case 'MONITORING':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-semibold';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-medium';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Consultation Telemetry</h3>
            <p className="text-[11px] text-slate-400">Objective Multi-Modal Session Summary</p>
          </div>
        </div>
        <span className={`text-[11px] px-2.5 py-1 rounded-full border ${getStatusBadge()}`}>
          {sessionStatus}
        </span>
      </div>

      {/* Main Objective Telemetry Summary Cards */}
      <div className="space-y-2.5 mb-3">
        {/* 1. Respiratory Summary */}
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0">
              <Wind className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-white block">Respiratory Telemetry</span>
              <span className="text-[10px] text-slate-400">
                Hand Gestures: <strong className="text-cyan-300">{telemetry.hand_gestures}</strong>
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="font-mono text-xs font-bold text-cyan-400 block">
              {telemetry.coughs} Coughs | {telemetry.sneezes} Sneezes
            </span>
            <span className="text-[10px] text-slate-500">Audio Captured</span>
          </div>
        </div>

        {/* 2. Emotion & Stress Summary */}
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
              <Smile className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-white block">Stress & Emotion</span>
              <span className="text-[10px] text-slate-400">
                Dominant: <strong className="text-indigo-300">{telemetry.dominant_emotion}</strong>
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="font-mono text-xs font-bold text-indigo-400 block">
              {telemetry.stress_score_pct}% Stress
            </span>
            <span className="text-[10px] text-slate-500">Affective Score</span>
          </div>
        </div>

        {/* 3. Fatigue & Yawn Summary */}
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0">
              <Clock className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-white block">Fatigue Telemetry</span>
              <span className="text-[10px] text-slate-400">
                Status: <strong className="text-amber-300">{telemetry.fatigue_status}</strong>
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="font-mono text-xs font-bold text-amber-400 block">
              {telemetry.yawn_count} Yawns
            </span>
            <span className="text-[10px] text-slate-500">MAR Analysis</span>
          </div>
        </div>
      </div>

      {/* Active Clinical Observations Ticker */}
      <div className="space-y-1.5">
        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
          Active Observations ({observations.length})
        </span>
        {observations.length > 0 ? (
          observations.map((obs, idx) => (
            <div key={idx} className="bg-amber-950/40 border border-amber-800/60 text-amber-200 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span className="truncate">{obs}</span>
            </div>
          ))
        ) : (
          <div className="bg-emerald-950/20 border border-emerald-800/40 text-emerald-300 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>All patient biometrics within baseline parameters.</span>
          </div>
        )}
      </div>
    </div>
  );
}

