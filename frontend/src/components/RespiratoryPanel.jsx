import React from 'react';
import { Wind, AlertCircle, Hand, Mic, Volume2 } from 'lucide-react';

// Real-Time Dynamic Voice Message Waveform Component
function AudioWaveform({ audioLevel = 0, isStreaming = false }) {
  const pattern = [
    0.25, 0.45, 0.75, 0.40, 0.65, 0.90, 1.0, 0.80, 0.55, 0.35, 
    0.60, 0.95, 0.70, 0.45, 0.85, 1.0, 0.65, 0.40, 0.75, 0.90, 
    0.50, 0.30, 0.70, 0.85, 0.40, 0.60, 0.35, 0.20
  ];

  return (
    <div className="flex items-center gap-[2.5px] h-5 px-1 flex-1 overflow-hidden">
      {pattern.map((ratio, i) => {
        const normLevel = isStreaming ? Math.min(100, audioLevel) / 100 : 0;
        // Dynamic bounce effect using sine variation + audio volume level
        const bounce = isStreaming && audioLevel > 5 ? Math.sin(i * 1.5 + Date.now() / 80) * 15 : 0;
        const activeHeight = isStreaming 
          ? Math.max(15, Math.min(100, (normLevel * 85 + 15) * ratio + bounce)) 
          : 20 * ratio;

        const isSpeaking = isStreaming && audioLevel > 5;
        const isLoud = isSpeaking && audioLevel > 40;

        return (
          <div
            key={i}
            className={`w-[2.5px] rounded-full transition-all duration-75 ${
              isLoud
                ? 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.6)]'
                : isSpeaking
                ? 'bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.6)]'
                : 'bg-slate-600/60'
            }`}
            style={{
              height: `${Math.max(12, Math.min(100, activeHeight))}%`,
            }}
          />
        );
      })}
    </div>
  );
}

export function RespiratoryPanel({ data, audioLevel = 0, isStreaming = false }) {
  const counts = data?.cumulative_counts || { cough: 0, sneeze: 0, sniffle: 0, hand_to_nose: 0 };
  const currentEvent = data?.respiratory_event || 'normal';
  const handToNose = data?.hand_to_nose_active || false;
  const handToNoseCount = data?.hand_to_nose_count || counts.hand_to_nose || 0;

  const [seconds, setSeconds] = React.useState(0);

  React.useEffect(() => {
    let timer;
    if (isStreaming) {
      timer = setInterval(() => setSeconds(s => s + 1), 1000);
    } else {
      setSeconds(0);
    }
    return () => clearInterval(timer);
  }, [isStreaming]);

  const formatTime = (sec) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

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

      {/* Real-time Voice Message Waveform Visualizer */}
      <div className="bg-[#0b1924]/90 p-2.5 px-3.5 rounded-xl border border-cyan-900/40 mb-3 flex items-center gap-3 shadow-inner">
        {/* Play / Mic Icon */}
        <div className="w-6 h-6 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
          {isStreaming && audioLevel > 5 ? (
            <Volume2 className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          ) : (
            <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-cyan-400 ml-0.5" />
          )}
        </div>

        {/* Waveform Bars Container */}
        <AudioWaveform audioLevel={audioLevel} isStreaming={isStreaming} />

        {/* Live Audio Timer & Status */}
        <div className="flex items-center gap-2 shrink-0">
          <span className="font-mono text-xs text-cyan-200/90 font-medium tracking-tight">
            {isStreaming ? (
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping inline-block" />
                {`${formatTime(seconds)} / 0:10`}
              </span>
            ) : (
              '0:00 / 0:10'
            )}
          </span>
          <span className="text-slate-500 text-xs hover:text-slate-300 transition-colors cursor-pointer">
            ✕
          </span>
        </div>
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
      <div className="grid grid-cols-2 gap-3">
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
      </div>
    </div>
  );
}
