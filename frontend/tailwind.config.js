/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand:   { DEFAULT: '#FF6B35', dark: '#e55a24' },
        dark:    { DEFAULT: '#1A1A2E' },
        cream:   { DEFAULT: '#FFF8F0' },
        success: { DEFAULT: '#2D6A4F' },
      },
      fontFamily: {
        sans:    ["'DM Sans'", "system-ui", "sans-serif"],
        display: ["'Playfair Display'", "serif"],
      },
      boxShadow: {
        'card':  '0 2px 12px rgba(26,26,46,0.06)',
        'float': '0 8px 32px rgba(26,26,46,0.15)',
      },
    },
  },
  plugins: [],
}
