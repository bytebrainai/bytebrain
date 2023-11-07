/** @type {import('tailwindcss').Config} */
module.exports = {
  prefix: "",
  corePlugins: {
    preflight: false,
  },
  darkMode: ["class", '[data-mode="dark"]'],
  content: ["./src/stories/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}

