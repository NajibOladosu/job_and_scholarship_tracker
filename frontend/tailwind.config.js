/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0A',
        surface: '#101010',
        border: '#1A1A1A',
        text: {
          primary: '#EDEDED',
          secondary: '#B5B5B5',
        },
        accent: {
          DEFAULT: '#00FF88',
          hover: '#00E67A',
          light: '#33FF9F',
        },
      },
      borderRadius: {
        DEFAULT: '1rem',
        lg: '1.25rem',
        xl: '1.5rem',
      },
      fontFamily: {
        sans: ['Manrope', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 12px rgba(0, 255, 136, 0.25)',
        'glow-lg': '0 0 24px rgba(0, 255, 136, 0.35)',
        'glow-xl': '0 0 36px rgba(0, 255, 136, 0.45)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 12px rgba(0, 255, 136, 0.25)' },
          '50%': { boxShadow: '0 0 24px rgba(0, 255, 136, 0.45)' },
        },
      },
    },
  },
  plugins: [],
}
