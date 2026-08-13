/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#090D16',
          card: '#121827',
          border: '#1E293B',
          muted: '#334155'
        },
        accent: {
          cyan: '#00F2FE',
          blue: '#4FACFE',
          rose: '#FF2E93',
          amber: '#F59E0B',
          emerald: '#10B981'
        }
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s infinite',
        'scan-line': 'scanLine 3s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 15px rgba(0, 242, 254, 0.4)' },
          '50%': { opacity: '0.6', boxShadow: '0 0 5px rgba(0, 242, 254, 0.1)' },
        },
        scanLine: {
          '0%': { top: '0%' },
          '100%': { top: '100%' }
        }
      }
    },
  },
  plugins: [],
}
