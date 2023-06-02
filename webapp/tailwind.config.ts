import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#71AE00",
        secondary: "#013443",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};

export default config;
