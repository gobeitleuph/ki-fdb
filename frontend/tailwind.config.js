/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1E466E',    // Dunkelblau
        accent: '#05C3DC',     // Türkis
        background: '#F2F2F2', // Hellgrau
        highlight: '#50FF59',  // Neongrün
        neutral: '#646464',    // Grau
        error: '#DC3545'       // Rot
      },
      fontFamily: {
        sans: ['"Trebuchet MS"', 'sans-serif']
      }
    }
  },
  plugins: []
}
