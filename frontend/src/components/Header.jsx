import React from 'react';
import { Activity, Wifi, WifiOff, ShieldCheck, HeartPulse } from 'lucide-react';

export function Header({ isConnected, isStreaming, fps, riskLevel = 'LOW' }) {
  const getRiskBadge = () => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  return (
    <header className="glass-panel sticky top-0 z-50 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
      {/* Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Activity className="w-6 h-6 text-slate-950 font-bold" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-['Outfit'] text-xl font-bold tracking-tight text-white">
              Med<span className="text-cyan-400">Watch</span>
            </h1>
            <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
              AI Clinical Monitoring
            </span>
          </div>
          <p className="text-xs text-slate-400">Real-Time Patient Consultation Engine</p>
        </div>
      </div>

      {/* Status Badges */}
      <div className="flex items-center gap-4">
        {/* Risk Level Badge */}
        <div className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all ${getRiskBadge()}`}>
          <HeartPulse className="w-4 h-4" />
          <span>Patient Status: {riskLevel}</span>
        </div>

        {/* Streaming Status */}
        <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-cyan-400 animate-ping' : 'bg-slate-600'}`} />
          <span className="text-slate-300 font-medium">{isStreaming ? `LIVE (${fps} FPS)` : 'OFFLINE'}</span>
        </div>

        {/* Backend Connection */}
        <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border ${
          isConnected 
            ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60' 
            : 'bg-red-950/40 text-red-400 border-red-800/60'
        }`}>
          {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          <span>{isConnected ? 'AI Engine Connected' : 'Engine Disconnected'}</span>
        </div>
      </div>
    </header>
  );
}
