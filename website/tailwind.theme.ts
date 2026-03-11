export const ecosystemTheme = {
  theme: {
    extend: {
      colors: {
        sun: {
          DEFAULT: "#FFC83D",
          soft: "#FFF4C2",
          warm: "#FFE27A",
          deep: "#E6B022",
        },
        science: {
          DEFAULT: "#2F6BFF",
          soft: "#EEF4FF",
          deep: "#1E4ED8",
        },
        ink: {
          DEFAULT: "#1F2937",
          muted: "#6B7280",
        },
        shell: {
          DEFAULT: "#FFFFFF",
          soft: "#FAFAFA",
          border: "#E5E7EB",
          strong: "#D8DDE6",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", '"Segoe UI"', "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Consolas", "monospace"],
      },
      borderRadius: {
        xl: "1.75rem",
        lg: "1.375rem",
        md: "1rem",
      },
      boxShadow: {
        soft: "0 10px 30px rgba(31, 41, 55, 0.06)",
        panel: "0 18px 60px rgba(31, 41, 55, 0.10)",
      },
      backgroundImage: {
        "sunrise-panel":
          "linear-gradient(145deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98)), linear-gradient(145deg, rgba(255,200,61,0.12), rgba(47,107,255,0.05))",
      },
    },
  },
} as const;

export default ecosystemTheme;
