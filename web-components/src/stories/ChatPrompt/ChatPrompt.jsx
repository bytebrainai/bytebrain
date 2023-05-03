import React from 'react';
import PropTypes from 'prop-types';
import './chatprompt.css';

/**
 * Primary UI component for user interaction
 */
export const ChatPrompt = ({ primary, backgroundColor, size, label, ...props }) => {
  const mode = primary ? 'storybook-button--primary' : 'storybook-button--secondary';
  return (
  <div
    class="bg-white text-black min-h-screen flex items-center justify-center"
  >
    <div class="lg:w-1/2 2xl:w-1/3 p-8 rounded-md bg-gray-100">
      <h1 class="text-3xl font-bold mb-6">
        Streaming OpenAI API Completions in JavaScript
      </h1>
      <div id="resultContainer" class="mt-4 h-48 overflow-y-auto">
        <p class="text-gray-500 text-sm mb-2">Generated Text</p>
        <p id="resultText" class="whitespace-pre-line"></p>
      </div>
      <input
        type="text"
        id="promptInput"
        class="w-full px-4 py-2 rounded-md bg-gray-200 placeholder-gray-500 focus:outline-none mt-4"
        placeholder="Enter prompt..."
      />
      <div class="flex justify-center mt-4">
        <button
          id="generateBtn"
          class="w-1/2 px-4 py-2 rounded-md bg-black text-white hover:bg-gray-900 focus:outline-none mr-2 disabled:opacity-75 disabled:cursor-not-allowed"
        >
          Generate
        </button>
        <button
          id="stopBtn"
          disabled
          class="w-1/2 px-4 py-2 rounded-md border border-gray-500 text-gray-500 hover:text-gray-700 hover:border-gray-700 focus:outline-none ml-2 disabled:opacity-75 disabled:cursor-not-allowed"
        >
          Stop
        </button>
      </div>
    </div>
  </div>
  );
};

ChatPrompt.propTypes = {
  /**
   * Is this the principal call to action on the page?
   */
  primary: PropTypes.bool,
  /**
   * What background color to use
   */
  backgroundColor: PropTypes.string,
  /**
   * How large should the button be?
   */
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  /**
   * Button contents
   */
  label: PropTypes.string.isRequired,
  /**
   * Optional click handler
   */
  onClick: PropTypes.func,
};

ChatPrompt.defaultProps = {
  backgroundColor: null,
  primary: false,
  size: 'medium',
  onClick: undefined,
};
