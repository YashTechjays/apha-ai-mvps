/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        apha: {
          DEFAULT: "#1B4F8A",
          50: "#EAF1F8",
          100: "#D5E3F1",
          200: "#A9C5E1",
          500: "#1B4F8A",
          600: "#163F6E",
          700: "#102E52",
          900: "#091A2D",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
