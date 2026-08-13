import React from 'react';
import { ShieldAlert, AlertCircle, CheckCircle } from 'lucide-react';

export function FusionRiskPanel({ data }) {
  const riskScore = Math.round((data?.overall_risk_score || 0) * 100);
  const riskLevel = data?.risk_level || 'LOW';
  const subScores = data?.sub_scores || { respiratory: 0.0, stress: 0.0, fatigue: 0.0 };
  const alerts = data?.active_alerts || [];

  const getRiskTheme = () => {
    switch (riskLevel) {
      case 'CRITICAL':
        return {
          bg: 'from-rose-600/20 to-red-950/80',
          border: 'border-rose-500/50',
          text: 'text-rose-400',
          meter: 'bg-gradient-to-r from-rose-500 to-red-600'
        };
      case 'HIGH':
        return {
          bg: 'from-amber-600/20 to-amber-950/80',
          border: 'border-amber-500/50',
          text: 'text-amber-400',
          meter: 'bg-gradient-to-r from-amber-500 to-rose-500'
        };
      case 'MEDIUM':
        return {
          bg: 'from-yellow-600/20 to-slate-900/80',
          border: 'border-yellow-500/50',
          text: 'text-yellow-400',
          meter: 'bg-gradient-to-r from-cyan-500 to-yellow-400'
        };
      default:
        return {
          bg: 'from-emerald-950/30 to-slate-900/80',
          border: 'border-emerald-500/30',
          text: 'text-emerald-400',
          meter: 'bg-gradient-to-r from-cyan-500 to-emerald-400'
        };
    }
  };

  const theme = getRiskTheme();

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white">Multi-Modal Fusion Risk</h3>
            <p className="text-[11px] text-slate-400">Unified Clinical Risk Assessment</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded-full border ${theme.border} ${theme.text} bg-slate-900/80`}>
          {riskLevel}
        </span>
      </div>

      {/* Main Overall Risk Score Gauge */}
      <div className={`p-4 rounded-xl border bg-gradient-to-b ${theme.bg} ${theme.border} mb-4 text-center relative overflow-hidden`}>
        <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400 block mb-1">
          Overall Clinical Risk Score
        </span>
        <div className="flex items-baseline justify-center gap-1 my-1">
          <span className={`font-['Outfit'] text-4xl font-extrabold ${theme.text}`}>{riskScore}</span>
          <span className="text-sm font-semibold text-slate-400">/ 100</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-900/80 overflow-hidden mt-3 border border-slate-800">
          <div
            className={`h-full transition-all duration-700 rounded-full ${theme.meter}`}
            style={{ width: `${riskScore}%` }}
          />
        </div>
      </div>

      {/* Sub-Scores Breakdown */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs mb-4">
        <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
          <span className="text-[10px] text-slate-400 block">Respiratory</span>
          <span className="font-mono font-bold text-slate-200">{Math.round((subScores.respiratory || 0) * 100)}%</span>
        </div>
        <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
          <span className="text-[10px] text-slate-400 block">Stress</span>
          <span className="font-mono font-bold text-slate-200">{Math.round((subScores.stress || 0) * 100)}%</span>
        </div>
        <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
          <span className="text-[10px] text-slate-400 block">Fatigue</span>
          <span className="font-mono font-bold text-slate-200">{Math.round((subScores.fatigue || 0) * 100)}%</span>
        </div>
      </div>

      {/* Active Alerts Ticker */}
      <div className="space-y-1.5">
        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
          Active Clinical Alerts ({alerts.length})
        </span>
        {alerts.length > 0 ? (
          alerts.map((alert, idx) => (
            <div key={idx} className="bg-rose-950/40 border border-rose-800/60 text-rose-200 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
              <span className="truncate">{alert}</span>
            </div>
          ))
        ) : (
          <div className="bg-emerald-950/20 border border-emerald-800/40 text-emerald-300 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>No critical alerts. Patient signals baseline normal.</span>
          </div>
        )}
      </div>
    </div>
  );
}
