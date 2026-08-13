import React from 'react';
import { Activity, AlertTriangle, Smile, Clock } from 'lucide-react';

export function FatiguePanel({ data }) {
  const status = data?.status || 'NORMAL';
  const mar = (data?.mar || 0.18).toFixed(2);
  const yawnCount = data?.yawn_count || 0;
  const isYawning = data?.is_yawning_now || false;

  const getStatusBadge = () => {
    if (status === 'FATIGUED' || isYawning) {
      return 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse font-bold';
    }
    if (status === 'MILDLY FATIGUED') {
      return 'bg-amber-500/20 text-amber-400 border-amber-500/40 font-semibold';
    }
    return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-medium';
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Fatigue Monitoring</h3>
            <p className="text-[11px] text-slate-400">Yawn Dynamics & MAR Analysis</p>
          </div>
        </div>
        <span className={`text-[11px] px-2.5 py-1 rounded-full border transition-all ${getStatusBadge()}`}>
          {status}
        </span>
      </div>

      {/* Yawn Frequency Gauge */}
      <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80 mb-4">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            Yawn Fatigue Frequency
          </span>
          <span className="font-mono font-bold text-amber-400">{yawnCount} Yawns</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden mb-1">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              yawnCount >= 3 || isYawning ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-gradient-to-r from-emerald-400 to-amber-400'
            }`}
            style={{ width: `${Math.min(100, Math.max(10, yawnCount * 33.3 + (isYawning ? 30 : 0)))}%` }}
          />
        </div>
        <span className="text-[10px] text-slate-500">Fatigue linked directly to cumulative yawn events</span>
      </div>

      {/* Yawn Counter & MAR Ratio */}
      <div className="grid grid-cols-2 gap-3">
        <div className={`p-3 rounded-xl border text-center transition-all ${
          isYawning ? 'bg-rose-950/60 border-rose-800/80 text-rose-300' : 'bg-slate-900/80 border-slate-800/80'
        }`}>
          <span className="text-[10px] text-slate-400 block mb-0.5 uppercase tracking-wider font-semibold">Cumulative Yawns</span>
          <span className={`font-mono text-xl font-bold ${isYawning ? 'text-rose-400' : 'text-amber-400'}`}>{yawnCount}</span>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800/80 text-center">
          <span className="text-[10px] text-slate-400 block mb-0.5 uppercase tracking-wider font-semibold">Mouth Ratio (MAR)</span>
          <span className="font-mono text-xl font-bold text-cyan-400">{mar}</span>
        </div>
      </div>

      {/* Active Yawn Alert Banner */}
      {isYawning && (
        <div className="mt-3 bg-rose-950/80 border border-rose-800 text-rose-200 px-3 py-2 rounded-lg text-xs flex items-center gap-2 animate-bounce font-medium">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>Patient Yawning Detected (Fatigue Indicator)</span>
        </div>
      )}
    </div>
  );
}
