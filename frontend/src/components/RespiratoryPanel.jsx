import React from 'react';
import { Wind, AlertCircle, Hand, Mic, Volume2 } from 'lucide-react';

export function RespiratoryPanel({ data, audioLevel = 0, isStreaming = false }) {
  const counts = data?.cumulative_counts || { cough: 0, sneeze: 0, sniffle: 0, hand_to_nose: 0 };
  const currentEvent = data?.respiratory_event || 'normal';
  const handToNose = data?.hand_to_nose_active || false;
  const handToNoseCount = data?.hand_to_nose_count || counts.hand_to_nose || 0;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Panel Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Wind className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Respiratory Health</h3>
            <p className="text-[11px] text-slate-400">Audio Events & Hand-to-Nose Gestures</p>
          </div>
        </div>
        <span className={`text-[11px] font-medium px-2.5 py-1 rounded-full border ${
          currentEvent !== 'normal'
            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse font-bold'
            : 'bg-slate-800 text-slate-400 border-slate-700'
        }`}>
          {currentEvent.toUpperCase()}
        </span>
      </div>

      {/* Real-time Microphone Audio Input Meter Bar */}
      <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 mb-3 flex items-center gap-2.5">
        <div className="flex items-center gap-1 text-[11px] text-slate-400 font-medium shrink-0">
          <Mic className={`w-3.5 h-3.5 ${isStreaming && audioLevel > 5 ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
          <span>Mic Audio</span>
        </div>
        <div className="flex-1 h-2 rounded-full bg-slate-800 overflow-hidden relative">
          <div
            className={`h-full transition-all duration-150 rounded-full ${
              audioLevel > 30 ? 'bg-gradient-to-r from-cyan-400 to-amber-400' : 'bg-cyan-500'
            }`}
            style={{ width: `${isStreaming ? Math.max(4, Math.min(100, audioLevel)) : 0}%` }}
          />
        </div>
        <span className="font-mono text-[10px] text-slate-400 w-8 text-right font-semibold">
          {isStreaming ? `${audioLevel}%` : 'OFF'}
        </span>
      </div>

      {/* Hand to Nose Status & Counter Card */}
      <div className={`p-3 rounded-xl border mb-3 flex items-center justify-between transition-all ${
        handToNose
          ? 'bg-rose-950/40 border-rose-800/60 text-rose-300'
          : 'bg-slate-900/60 border-slate-800 text-slate-400'
      }`}>
        <div className="flex items-center gap-2.5">
          <Hand className={`w-4 h-4 ${handToNose ? 'text-rose-400 animate-bounce' : 'text-slate-500'}`} />
          <div>
            <span className="text-xs font-medium block">Hand-to-Nose Gesture</span>
            <span className="text-[10px] text-slate-400">Total Count: <strong className="text-rose-400 font-mono">{handToNoseCount}</strong></span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800/90 text-rose-400 border border-rose-900/40">
            {handToNoseCount} {handToNoseCount === 1 ? 'Time' : 'Times'}
          </span>
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
            handToNose ? 'bg-rose-900/80 text-rose-200' : 'bg-slate-800 text-slate-500'
          }`}>
            {handToNose ? 'DETECTED' : 'INACTIVE'}
          </span>
        </div>
      </div>

      {/* Cumulative Counters Grid */}
      <div className="grid grid-cols-3 gap-3">
        {/* Cough */}
        <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800/80 text-center">
          <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block mb-1">Coughs</span>
          <span className="font-['Outfit'] text-xl font-bold text-cyan-400">{counts.cough}</span>
        </div>

        {/* Sneeze */}
        <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800/80 text-center">
          <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block mb-1">Sneezes</span>
          <span className="font-['Outfit'] text-xl font-bold text-cyan-400">{counts.sneeze}</span>
        </div>

        {/* Sniffle */}
        <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800/80 text-center">
          <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block mb-1">Sniffles</span>
          <span className="font-['Outfit'] text-xl font-bold text-cyan-400">{counts.sniffle}</span>
        </div>
      </div>
    </div>
  );
}
