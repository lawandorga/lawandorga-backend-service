module.exports = {
  content: [
    "templates/**/*.html",
      "templates/**/*.class",
    // "node_modules/@lawandorga/components/dist/es.js",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        lorgablue: "#003c4d",
        // design tokens of the auth pages (see static/src/tailwind.css)
        "lo-petrol": "#003c4d",
        "lo-petrol-hover": "#00566e",
        "lo-accent": "#9cbcc6",
        "lo-mist": "#e4f1f3",
        "lo-text": "#14212b",
        "lo-text-2": "#2c3a44",
        "lo-muted": "#3d4b55",
        "lo-input": "#7b8790",
        "lo-error": "#b42318",
        blue: {
          50: "#eff9fb",
          100: "#d0e7ed",
          200: "#aad0db",
          300: "#8abbc9",
          400: "#6ca7b7",
          500: "#428193",
          600: "#275f6f",
          700: "#153f4b",
          800: "#0a2027",
          900: "#010203",
        },
      },
      // typography: (theme: any) => ({  // eslint-disable-line
      //   DEFAULT: {
      //     css: {
      //       table: {},
      //       thead: {
      //         border: "none",
      //       },
      //       tr: {
      //         border: "none",
      //       },
      //       "tr:last-child": {
      //         borderBottomWidth: "0",
      //       },
      //       th: {
      //         verticalAlign: "bottom",
      //         borderWidth: "2px",
      //         borderColor: theme("colors.gray[400]"),
      //         backgroundColor: theme("colors.gray[200]"),
      //         padding: "4px 8px",
      //       },
      //       "th > p, td > p": {
      //         margin: 0,
      //       },
      //       td: {
      //         verticalAlign: "top",
      //         borderWidth: "2px",
      //         borderColor: theme("colors.gray[300]"),
      //         backgroundColor: theme("colors.gray[100]"),
      //       },
      //       "tbody td:first-child": {
      //         paddingLeft: "auto",
      //       },
      //     },
      //   },
      // }),
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    // require("@tailwindcss/forms"),
  ],
};
