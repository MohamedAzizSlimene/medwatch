import { useState, useEffect, useRef, useCallback } from 'react';

export function useMedWatchStream(wsUrl = 'ws://localhost:8000/ws/stream') {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState(null);
  const [fps, setFps] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0); // Live mic volume level 0-100%

  const [predictions, setPredictions] = useState({
    respiratory: {
      respiratory_event: 'normal',
      hand_to_nose_active: false,
      hand_to_nose_count: 0,
      cumulative_counts: { cough: 0, sneeze: 0, sniffle: 0, hand_to_nose: 0 }
    },
    emotion: {
      dominant_emotion: 'Neutral',
      confidence: 0.95,
      clinical_stress_score: 0.05,
      distribution: { Neutral: 0.95, Happy: 0.01, Sad: 0.01, Surprise: 0.01, Fear: 0.01, Disgust: 0.005, Angry: 0.005 }
    },
    fatigue: {
      perclos_score: 0.03,
      status: 'NORMAL',
      ear: 0.32,
      mar: 0.16,
      yawn_count: 0,
      is_yawning_now: false
    },
    fusion: {
      overall_risk_score: 0.05,
      risk_level: 'LOW',
      active_alerts: []
    }
  });

  const socketRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const frameCountRef = useRef(0);
  const fpsTimerRef = useRef(null);

  // Audio Context & Buffer Refs
  const audioContextRef = useRef(null);
  const audioProcessorRef = useRef(null);
  const audioBufferRef = useRef([]);

  // Zero-Lag non-blocking ref: prevents queue backlog completely
  const isProcessingRef = useRef(false);

  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        setStreamError(null);
        isProcessingRef.current = false;
        console.log('[MedWatch WS] Connected to backend server');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && !data.error) {
            setPredictions(data);
            frameCountRef.current += 1;
          }
        } catch (e) {
          console.error('[MedWatch WS] Parse error:', e);
        } finally {
          isProcessingRef.current = false;
        }
      };

      ws.onerror = (err) => {
        console.error('[MedWatch WS] Error:', err);
        setStreamError('WebSocket connection error. Ensure AI backend server is running on port 8000.');
        setIsConnected(false);
        isProcessingRef.current = false;
      };

      ws.onclose = () => {
        setIsConnected(false);
        isProcessingRef.current = false;
        console.log('[MedWatch WS] Connection closed');
      };

      socketRef.current = ws;
    } catch (err) {
      setStreamError('Failed to initiate WebSocket connection.');
    }
  }, [wsUrl]);

  useEffect(() => {
    fpsTimerRef.current = setInterval(() => {
      setFps(frameCountRef.current);
      frameCountRef.current = 0;
    }, 1000);

    return () => clearInterval(fpsTimerRef.current);
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connectWebSocket]);

  // Downsample native float32 buffer to exact 16,000 Hz target sample rate
  const resampleTo16kHz = (inputSamples, inputSampleRate) => {
    if (inputSampleRate === 16000) return inputSamples;

    const ratio = inputSampleRate / 16000;
    const newLength = Math.round(inputSamples.length / ratio);
    const result = new Float32Array(newLength);

    for (let i = 0; i < newLength; i++) {
      const originIndex = i * ratio;
      const indexFloor = Math.floor(originIndex);
      const indexCeil = Math.min(inputSamples.length - 1, Math.ceil(originIndex));
      const fraction = originIndex - indexFloor;

      result[i] = inputSamples[indexFloor] * (1 - fraction) + inputSamples[indexCeil] * fraction;
    }
    return result;
  };

  const float32ToBase64 = (float32Array) => {
    const buffer = new ArrayBuffer(float32Array.length * 4);
    const view = new DataView(buffer);
    for (let i = 0; i < float32Array.length; i++) {
      view.setFloat32(i * 4, float32Array[i], true);
    }
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  };

  const startStream = async () => {
    try {
      setStreamError(null);

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { max: 15 } },
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        await videoRef.current.play();
      }

      // Audio Capture & 16kHz Resampling
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const audioCtx = new AudioContext();
        const nativeSampleRate = audioCtx.sampleRate;

        const source = audioCtx.createMediaStreamSource(mediaStream);
        const processor = audioCtx.createScriptProcessor(4096, 1, 1);

        audioBufferRef.current = [];

        processor.onaudioprocess = (e) => {
          const inputData = e.inputBuffer.getChannelData(0);

          // Calculate RMS volume level for UI meter
          let sumSquares = 0;
          for (let i = 0; i < inputData.length; i++) {
            sumSquares += inputData[i] * inputData[i];
          }
          const rms = Math.sqrt(sumSquares / inputData.length);
          const level = Math.min(100, Math.round(rms * 400));
          setAudioLevel(level);

          // Downsample block to 16kHz
          const resampledBlock = resampleTo16kHz(inputData, nativeSampleRate);
          audioBufferRef.current.push(...resampledBlock);

          // Keep 1.0 second rolling window (16,000 samples)
          if (audioBufferRef.current.length > 16000) {
            audioBufferRef.current = audioBufferRef.current.slice(-16000);
          }
        };

        source.connect(processor);
        processor.connect(audioCtx.destination);

        audioContextRef.current = audioCtx;
        audioProcessorRef.current = processor;
      } catch (audioErr) {
        console.warn('[MedWatch] Audio capture setup warning:', audioErr);
      }

      setIsStreaming(true);

      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas');
        canvasRef.current.width = 640;
        canvasRef.current.height = 480;
      }

      // Fast streaming check loop (every 100ms)
      intervalRef.current = setInterval(() => {
        if (!videoRef.current || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
          return;
        }

        if (isProcessingRef.current) {
          return;
        }

        isProcessingRef.current = true;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        const dataUrl = canvas.toDataURL('image/jpeg', 0.5);
        const base64Frame = dataUrl.split(',')[1];

        let base64Audio = null;
        if (audioBufferRef.current.length >= 8000) {
          const audioChunk = new Float32Array(audioBufferRef.current);
          base64Audio = float32ToBase64(audioChunk);
        }

        socketRef.current.send(JSON.stringify({
          frame_b64: base64Frame,
          audio_b64: base64Audio
        }));
      }, 100);

    } catch (err) {
      console.error('[MedWatch] Webcam/Mic error:', err);
      setStreamError('Could not access camera or microphone. Please check browser permissions.');
      setIsStreaming(false);
    }
  };

  const stopStream = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    if (audioProcessorRef.current) {
      audioProcessorRef.current.disconnect();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setAudioLevel(0);
    isProcessingRef.current = false;
  };

  return {
    videoRef,
    isConnected,
    isStreaming,
    streamError,
    predictions,
    fps,
    audioLevel,
    startStream,
    stopStream,
    reconnect: connectWebSocket
  };
}
