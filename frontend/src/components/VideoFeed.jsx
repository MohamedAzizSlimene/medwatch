import React from 'react';
import { Camera, AlertTriangle, Eye, Sparkles } from 'lucide-react';

export function VideoFeed({ videoRef, isStreaming, predictions, error, onStart }) {
  const handToNoseActive = predictions?.respiratory?.hand_to_nose_active;
  const handToNoseCount = predictions?.respiratory?.hand_to_nose_count || predictions?.respiratory?.cumulative_counts?.hand_to_nose || 0;
  const dominantEmotion = predictions?.emotion?.dominant_emotion || 'Neutral';
  const stressScore = Math.round((predictions?.emotion?.clinical_stress_score || 0) * 100);
  const fatigueStatus = predictions?.fatigue?.status || 'Alert';

  return (
    <div className="glass-panel rounded-2xl p-4 border border-slate-800 relative overflow-hidden flex flex-col items-center justify-center min-h-[420px]">
      {/* Hand-to-Nose Active Overlay Banner */}
      {isStreaming && handToNoseActive && (
        <div className="absolute top-6 left-6 right-6 z-20 bg-rose-950/90 border border-rose-500/60 text-rose-200 px-4 py-2.5 rounded-xl shadow-xl flex items-center justify-between backdrop-blur-md animate-bounce">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
            <span>Hand-to-Nose Activity Detected (Respiratory Risk Gesture)</span>
          </div>
          <span className="text-xs bg-rose-900/80 px-2.5 py-0.5 rounded font-mono font-bold text-rose-200">
            Count: #{handToNoseCount}
          </span>
        </div>
      )}

      {/* Video Container */}
      <div className="relative w-full h-full rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center">
        {/* Live Video */}
        <video
          ref={videoRef}
          className={`w-full h-full object-cover transition-opacity duration-300 ${isStreaming ? 'opacity-100' : 'opacity-0'}`}
          playsInline
          muted
        />

        {/* Placeholder when not streaming */}
        {!isStreaming && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center bg-gradient-to-b from-slate-900 to-slate-950">
            <div className="w-16 h-16 rounded-2xl bg-cyan-950/50 border border-cyan-800/60 flex items-center justify-center mb-4 text-cyan-400 shadow-lg shadow-cyan-500/10">
              <Camera className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Webcam Feed Inactive</h3>
            <p className="text-xs text-slate-400 max-w-sm mb-6">
              Start the consultation stream to begin real-time AI monitoring of patient emotion, respiratory sounds, and fatigue levels.
            </p>
            {error && (
              <div className="mb-4 text-xs text-rose-400 bg-rose-950/60 border border-rose-800/60 px-3 py-2 rounded-lg">
                {error}
              </div>
            )}
            <button
              onClick={onStart}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-semibold text-sm shadow-lg shadow-cyan-500/25 hover:brightness-110 active:scale-95 transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 fill-slate-950" />
              Start Live Camera Stream
            </button>
          </div>
        )}

        {/* Live HUD Overlay when streaming */}
        {isStreaming && (
          <div className="absolute bottom-4 left-4 right-4 z-10 flex items-center justify-between pointer-events-none">
            {/* Bottom-left: Dominant Emotion & Stress */}
            <div className="bg-slate-950/80 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-800/80 text-xs flex items-center gap-3">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Emotion</span>
                <span className="font-semibold text-cyan-400">{dominantEmotion}</span>
              </div>
              <div className="w-px h-6 bg-slate-800" />
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Stress Level</span>
                <span className={`font-semibold ${stressScore > 50 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {stressScore}%
                </span>
              </div>
            </div>

            {/* Bottom-right: Fatigue Badge */}
            <div className="bg-slate-950/80 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-800/80 text-xs flex items-center gap-2">
              <Eye className="w-4 h-4 text-slate-400" />
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Fatigue Status</span>
                <span className={`font-semibold ${fatigueStatus.includes('FATIGUED') ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {fatigueStatus}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
