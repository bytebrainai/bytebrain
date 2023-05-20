import React from 'react';
import ChatMessage from './ChatMessage';

export const ChatPrompt = (props) => {
  const { 
    title = 'ChatBot', 
    defaultQuestion = 'Send your message', 
    websocketHost,
    websocketPort,
    websocketEndpoint 
  } = props
  const [question, setQuestion] = React.useState('');
  const [messages, setMessages] = React.useState([]);

  const handleChange = (event) => {
    setQuestion(event.target.value)
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    handleClick();
    event.target.reset();
  }

  const handleClick = () => {
    const ws = new WebSocket("ws://" + (websocketHost || window.location.hostname) + ":" + websocketPort + websocketEndpoint)
    ws.onopen = (event) => {
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
      <div className="justify-between flex flex-col h-screen w-full p-5 rounded-md bg-gray-100 overflow-auto">
        <h1 className="text-orange-600 text-3xl font-bold mb-6">
          {title}
        </h1>
        <div
          id="messages"
          className="flex flex-col space-y-4 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
          {
            messages.map((m, id) =>
              <ChatMessage key={id} userType={m.userType} text={m.message} />
            )
          }
        </div>
        <form onSubmit={handleSubmit} className="flex bottom-5 left-5 right-5 h-10 mt-4">
          <input
            type="text"
            id="promptInput"
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-md bg-gray-200 placeholder-gray-500 focus:outline-none"
            placeholder={defaultQuestion}
          />
          <button
            id="generateBtn"
            type='submit'
            className="px-6 rounded-md bg-black text-white hover:bg-gray-900 focus:outline-none disabled:opacity-75 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPrompt