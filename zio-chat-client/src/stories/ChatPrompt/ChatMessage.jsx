import React from 'react';
import bot from './bot.png';
import user from './user.png';
import ReactMarkdown from 'react-markdown'
import hljs from "highlight.js";
import { useEffect } from 'react';
import "highlight.js/styles/github.css";

function ChatMessage(props) {
  useEffect(() => {
    if (props.highlight && props.userType === "bot") {
      hljs.highlightAll();
    }
  });

  let chatMessage;
  if (props.userType === "user") {
    chatMessage =
      <div className="chat-message">
        <div className="flex items-end">
          <div className="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
            <div>
              <span className=
                "px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">
                <ReactMarkdown>{props.text}</ReactMarkdown>
              </span>
            </div>
          </div>
          <img src={user} alt="User Profile" className="w-6 h-6 rounded-full order-1" />
        </div>
      </div>
  } else if (props.userType === "bot") {
    chatMessage =
      <div className="chat-message">
        <div className="flex items-end">
          <div className="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
            <div>
              <span className="px-4 py-2 space-y-2 rounded-lg inline-block rounded-br-none bg-blue-600 text-white">
                <ReactMarkdown>{props.text}</ReactMarkdown>
              </span>
            </div>
          </div>
          <img src={bot} alt="Robot Profile" className="w-6 h-6 rounded-full order-1" />
        </div>
      </div>
  }
  return (chatMessage)
}

export default ChatMessage