import React from 'react';
import { useMedWatchStream } from './hooks/useMedWatchStream';
import { Header } from './components/Header';
import { VideoFeed } from './components/VideoFeed';
import { RespiratoryPanel } from './components/RespiratoryPanel';
import { EmotionPanel } from './components/EmotionPanel';
import { FatiguePanel } from './components/FatiguePanel';
import { FusionRiskPanel } from './components/FusionRiskPanel';
import { SessionControls } from './components/SessionControls';

export default function App() {
  const {
    videoRef,
    isConnected,
    isStreaming,
    streamError,
    predictions,
    fps,
    audioLevel,
    startStream,
    stopStream,
    reconnect
  } = useMedWatchStream();

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex flex-col">
      {/* Header */}
      <Header
        isConnected={isConnected}
        isStreaming={isStreaming}
        fps={fps}
        riskLevel={predictions?.fusion?.risk_level}
      />

      {/* Main Clinical Dashboard Content */}
      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Live Webcam Stream & Controls (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <VideoFeed
            videoRef={videoRef}
            isStreaming={isStreaming}
            predictions={predictions}
            error={streamError}
            onStart={startStream}
          />

          <SessionControls
            isStreaming={isStreaming}
            isConnected={isConnected}
            onStart={startStream}
            onStop={stopStream}
            onReconnect={reconnect}
          />
        </div>

        {/* Right Column: 4 Real-Time Analytics Panels (5 cols) */}
        <div className="lg:col-span-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Respiratory Panel */}
          <RespiratoryPanel
            data={predictions?.respiratory}
            audioLevel={audioLevel}
            isStreaming={isStreaming}
          />

          {/* Emotion Panel */}
          <EmotionPanel data={predictions?.emotion} />

          {/* Fatigue Panel */}
          <FatiguePanel data={predictions?.fatigue} />

          {/* Fusion Risk Panel */}
          <FusionRiskPanel data={predictions?.fusion} />
        </div>
      </main>
    </div>
  );
}
