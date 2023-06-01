import React from 'react';
import ChatMessage from './ChatMessage';
import './ChatPrompt.css'

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

  function isButtonDisabled() {
    if (messages.length === 0) { return false }
    else if (messages[messages.length - 1].userType == "user") { return true }
    else if (messages[messages.length - 1].userType == "bot"){
      return !messages[messages.length - 1].completed ? true : false
    }
  }

  const handleClick = () => {
    const host = websocketHost || window.location.hostname;
    const port = websocketPort === "80" ? "" : ":" + websocketPort;
    const protocol = websocketPort === "80" ? "wss://" : "ws://";
    const ws = new WebSocket(protocol + host+ port + websocketEndpoint);
    ws.onopen = (event) => {
      setMessages(messages => messages.concat([
        {
          userType: "user",
          message: question,
          completed: true
        }
      ]));
      const history = messages.map(m => m.message);
      const data = {
        "question": question,
        "history": history
      }
      ws.send(JSON.stringify(data));
    };
    ws.onmessage = function (event) {
      const result = JSON.parse(event.data)
      const word = result.token;
      const completed = result.completed;
      setMessages(messages => {
        if (
          messages.length === 0 ||
          messages[messages.length - 1].userType === "user"
        ) {
          return [...messages, { userType: "bot", message: word, completed: completed }];
        } else {
          const updatedMessages = [...messages];
          updatedMessages[updatedMessages.length - 1] = {
            ...updatedMessages[updatedMessages.length - 1],
            message: updatedMessages[updatedMessages.length - 1].message + word,
            completed: completed
          };
          return updatedMessages;
        }
      });
    };
  }

  return (
    <div>
      <div className="justify-between flex flex-col h-screen w-full p-5 rounded-md bg-gray-100 overflow-auto">
        <h1 className="text-orange-600 text-3xl font-bold mb-6">
          {title}
        </h1>
        <div
          id="scroller"
          className="flex flex-col space-y-4 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch scroll-smooth">
          {
            messages.map((m, id) =>
              <ChatMessage key={id} id={"chat" + id} userType={m.userType} text={m.message} highlight={m.completed} />
            )
          }
          <div id="anchor"></div>
        </div>
        <form onSubmit={handleSubmit} className="flex bottom-5 left-5 right-5 h-10 mt-4">
          <input
            type="text"
            id="promptInput"
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-md bg-gray-200 placeholder-gray-500 focus:outline-none"
            placeholder={defaultQuestion}
          />
          <button disabled={isButtonDisabled()}
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