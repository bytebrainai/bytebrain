import React from 'react';
import ChatMessage from './ChatMessage';

export const ChatPrompt = () => {
  const [question, setQuestion] = React.useState('');
  const [messages, setMessages] = React.useState([]);

  const handleChange = (event) => {
    setQuestion(event.target.value)
  }

  const handleClick= () => {
    const ws = new WebSocket('ws://localhost:8081/chat')
    ws.onopen = (event) => {
      console.log(question)
      setMessages(messages => messages.concat([
        {
          userType: "user",
          message: question
        }
      ]));
      ws.send(question);
    };
    ws.onmessage = function (event) {
      const response = JSON.parse(event.data).result;
      setMessages(messages => messages.concat([{
        userType: "bot",
        message: response
      }]));
    };
  }


  return (
    <div>
      <div className="w-full p-5 rounded-md bg-gray-100 h-screen relative">
        <h1 className="text-orange-600 text-3xl font-bold mb-6">
          ZIO Chat
        </h1>
        <div id="resultContainer" className="mt-4 h-fit overflow-y-auto">
          <div id="messages" className="flex flex-col space-y-4 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
            {
              messages.map((m, id) =>
                <ChatMessage key={id} userType={m.userType} text={m.message} />
              )
            }
          </div>
        </div>
        <div className="flex absolute bottom-5 left-5 right-5 h-10">
        <input
          type="text"
          id="promptInput"
          value={question}
          onChange={handleChange}
          className="w-full px-4 rounded-md bg-gray-200 placeholder-gray-500 focus:outline-none"
          placeholder="Write your question about ZIO"
        />
          <button
            id="generateBtn"
            className="px-6 rounded-md bg-black text-white hover:bg-gray-900 focus:outline-none disabled:opacity-75 disabled:cursor-not-allowed"
            onClick={handleClick}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPrompt