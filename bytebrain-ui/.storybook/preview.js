import "../src/index.css";

/** @type { import('@storybook/react').Preview } */
const preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
  globalTypes: {
    darkMode: {
      defaultValue: true, // Enable dark mode by default on all stories
    },
    // Optional (Default: 'dark')
    className: {
      defaultValue: "dark", // Set your custom dark mode class name
    },
  },
};

export default preview;

import React from "react";
import { useDarkMode } from "storybook-dark-mode";

export const decorators = [
  (Story) => {
    const mode = useDarkMode() ? "dark" : "light";
    return (
      <div data-theme={mode}>
        <Story />
      </div>
    );
  },
];
