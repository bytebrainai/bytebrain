import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import React, { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import FeedbackForm from "../FeedbackForm";
import bot from './bot.png';
import user from './user.png';
import RelatedQuestions from "./RelatedQuestions";
import References from "./References";

function ChatMessage(props) {
  const [chatHistory, setChatHistory] = React.useState(props.chatHistory);

  function remove_number_fromHead(string) {
    const regex = /^\d+\.|[*-]\s*/;
    return string.replace(regex, '');
  }

  function extract_numbered_lines(string) {
    const regex = /\n/;
    let lines =
      string
        .split(regex)
        .filter(line => line.length > 0)
        .map((l) => l.trim())
        .filter(line => /\d+|[*-]/.test(line));
    return lines;
  }


  useEffect(() => {
    if (props.highlight && props.userType === "bot") {
      document
        .querySelectorAll<HTMLElement>("#" + props.id + " pre code")
        .forEach((el) => {
          hljs.highlightElement(el);
        });
    }
  });

  useEffect(() => {
    setChatHistory(props.chatHistory);
  }, [props]);

  let chatMessage;
  if (props.userType === "user") {
    chatMessage =
      <div className="w-full chat-message user-message text-base flex flex-row space-x-2" id={props.id} >
        <img src={user} alt="User Profile" className="w-6 h-6 rounded-full" />
        <ReactMarkdown className='px-4 py-2 rounded-lg rounded-bl-none bg-gray-300 text-gray-600'>{props.text}</ReactMarkdown>
      </div>
  } else if (props.userType === "bot") {
    if (String(props.text).includes('Related Questions:')) {
      let response = props.text.split('Related Questions:')
      let related_questions = extract_numbered_lines(response[1].trim()).map((item) => remove_number_fromHead(item))
      chatMessage =
        <div className="w-full chat-message bot-message text-base flex flex-row space-x-2" id={props.id}>
          <img src={bot} alt="Robot Profile" className="w-6 h-6 rounded-full" />
          <div className="w-full">
            <ReactMarkdown className='px-4 py-2 space-y-2 rounded-t-lg bg-blue-600 text-white'>{response[0]}</ReactMarkdown>
            <RelatedQuestions items={related_questions} setQuestion={props.setQuestion} />
            <References items={props.references} />
          </div>
          <FeedbackForm chatHistory={chatHistory.slice(1, props.index + 1)} baseHttpUrl={props.baseHttpUrl} />
        </div>
    } else {
      chatMessage =
        <div className="w-full chat-message bot-message text-base flex flex-row space-x-2" id={props.id}>
          <img src={bot} alt="Robot Profile" className="w-6 h-6 rounded-full" />
          <div className="w-full">
            <ReactMarkdown className='px-4 py-2 space-y-2 rounded-t-lg bg-blue-600 text-white'>{props.text}</ReactMarkdown>
            <References items={props.references} />
          </div>
          <FeedbackForm chatHistory={chatHistory.slice(1, props.index + 1)} baseHttpUrl={props.baseHttpUrl} />
        </div>
    }
  }

  return (chatMessage)
}

export default ChatMessage;
