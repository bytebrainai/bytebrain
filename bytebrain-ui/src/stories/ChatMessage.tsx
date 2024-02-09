/**
 * Copyright 2023-2024 ByteBrain AI
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import FeedbackForm from "./FeedbackForm";
import Bot from './Bot';
import User from './User';
import user from './user.png';
import RelatedQuestions from "./RelatedQuestions";
import References from "./References";
import { ReferenceItem } from "./References";
import Message from "./Message";
import UserTypes from "./UserTypes";

interface ChatMessageProps {
  id: string;
  chatHistory: Message[];
  highlight: boolean;
  userType: UserTypes;
  text: string;
  setQuestion: React.Dispatch<React.SetStateAction<string>>;
  references: ReferenceItem[];
  baseHttpUrl: string;
  index: number;
}

const ChatMessage: React.FC<ChatMessageProps> = (props: ChatMessageProps) => {
  const [chatHistory, setChatHistory] = useState<Message[]>(props.chatHistory);

  function remove_number_fromHead(string: string): string {
    const regex = /^\d+\.|[*-]\s*/;
    return string.replace(regex, '');
  }

  function extract_numbered_lines(string: string): string[] {
    const regex = /\n/;
    const lines = string
      .split(regex)
      .filter(line => line.length > 0)
      .map((l) => l.trim())
      .filter(line => /\d+|[*-]/.test(line));
    return lines;
  }

  useEffect(() => {
    if (props.highlight && props.userType === UserTypes.Bot) {
      document
        .querySelectorAll<HTMLElement>("#" + props.id + " pre code")
        .forEach((el) => {
          hljs.highlightElement(el);
        });
    }
  }, [props.highlight, props.userType, props.id]);

  useEffect(() => {
    setChatHistory(props.chatHistory);
  }, [props]);

  let chatMessage: JSX.Element | null = null;

  if (props.userType === UserTypes.User) {
    chatMessage = (
      <div className="w-full chat-message user-message text-base flex flex-row space-x-2" id={props.id}>
        <User />
        <ReactMarkdown className='px-4 py-2 rounded-lg rounded-bl-none bg-gray-300 text-gray-600'>{props.text}</ReactMarkdown>
      </div>
    );
  } else if (props.userType === UserTypes.Bot) {
    if (String(props.text).includes('Related Questions:')) {
      const response = props.text.split('Related Questions:');
      const related_questions = extract_numbered_lines(response[1].trim()).map((item) => remove_number_fromHead(item));
      chatMessage = (
        <div className="w-full chat-message bot-message text-base flex flex-row space-x-2" id={props.id}>
          <Bot />
          <div className="w-full">
            <ReactMarkdown className='px-4 py-2 space-y-2 rounded-t-lg bg-blue-600 text-white'>{response[0]}</ReactMarkdown>
            <RelatedQuestions items={related_questions} setQuestion={props.setQuestion} />
            <References items={props.references} />
          </div>
          <FeedbackForm chatHistory={chatHistory.slice(1, props.index + 1)} baseHttpUrl={props.baseHttpUrl} />
        </div>
      );
    } else {
      chatMessage = (
        <div className="w-full chat-message bot-message text-base flex flex-row space-x-2" id={props.id}>
          <Bot />
          <div className="w-full">
            <ReactMarkdown className='px-4 py-2 space-y-2 rounded-t-lg bg-blue-600 text-white'>{props.text}</ReactMarkdown>
            <References items={props.references} />
          </div>
          <FeedbackForm chatHistory={chatHistory.slice(1, props.index + 1)} baseHttpUrl={props.baseHttpUrl} />
        </div>
      );
    }
  }

  return chatMessage;
}

export default ChatMessage;
