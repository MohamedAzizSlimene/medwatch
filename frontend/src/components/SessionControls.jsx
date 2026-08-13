import React from 'react';
import { Play, Square, RefreshCw } from 'lucide-react';

export function SessionControls({ isStreaming, isConnected, onStart, onStop, onReconnect }) {
  return (
    <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {!isStreaming ? (
          <button
            onClick={onStart}
            disabled={!isConnected}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-semibold text-sm shadow-lg shadow-cyan-500/25 hover:brightness-110 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4 fill-slate-950" />
            Start Consultation Stream
          </button>
        ) : (
          <button
            onClick={onStop}
            className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm shadow-lg shadow-rose-600/25 active:scale-95 transition-all flex items-center gap-2"
          >
            <Square className="w-4 h-4 fill-white" />
            Stop Consultation Stream
          </button>
        )}
      </div>

      <button
        onClick={onReconnect}
        className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-all flex items-center gap-2"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        Reconnect AI Engine
      </button>
    </div>
  );
}
