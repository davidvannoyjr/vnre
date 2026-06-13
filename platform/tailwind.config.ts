import type { Config } from "tailwindcss";

// Palette mirrors VNRE branding: neutral steel base, red as accent only.
const config: Config = {
  content: [
    "./src/**/*.{ts,tsx,mdx}",
    "./content/**/*.{md,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        steel: "#2A2A2A",
        band: "#EDEDED",
        strip: "#F4F4F4",
        accent: "#C8102E"
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
