import React from 'react';
import ChatMessage from './ChatMessage';
import './ChatPrompt.css'
import { useEffect } from 'react';

export const ChatPrompt = (props) => {

  const greetings = [
    {
      userType: "bot",
      message: "🌟 Greetings from ZIO Chat! 🌟 Have questions about ZIO? Look no further! I'm here to be your ZIO guru. Whether you're a seasoned pro or just starting out, I've got answers tailored just for you. Fire away with your ZIO queries, and I'll hit you back with the best insights I've got. Let's dive into the world of ZIO together!",
      completed: true
    },
    {
      userType: "bot",
      message: "🔥 Ignite your ZIO journey with ZIO Chat! 🔥 Ready to unravel the intricacies of ZIO? As your trusty sidekick, I'm here to light the way. No matter if you're wandering through functional forests or traversing effectful landscapes, I've got answers to keep you on track. Your ZIO adventure starts here – ask me anything and let's explore together!",
      completed: true
    },
    {
      userType: "bot",
      message: "Hello! 😊 I'm your ZIO Chat Bot, designed to be your go-to resource for all things ZIO! Whether you're new to this powerful functional effect system or a seasoned pro, I'm here to assist you. ZIO empowers you to build concurrent and resilient applications in Scala, offering referential transparency, composable data types, type-safety, and more. So, go ahead and ask me anything about ZIO – I'm here to provide the answers you need! 🤖",
      completed: true
    },
    {
      userType: "bot",
      message: "Hi there! 👋 I'm ZIO Chat, your friendly neighborhood ZIO expert. I'm here to help you navigate the world of ZIO. Whether you're a seasoned pro or just starting out, fire away with your ZIO questions. I will hit you back with the best insights I've got. Let's dive into the world of ZIO together!",
      completed: true
    },
    {
      userType: "bot",
      message: "🎉 Hey there, ZIO aficionado! 🎉 Step into the ZIO wonderland with me as your guide. Whether you're a functional fanatic or just dipping your toes into the ZIO ecosystem, I'm here to make your journey smooth. Got ZIO questions? I've got answers! Let's navigate the ZIO universe together and unlock its infinite possibilities!",
      completed: true
    },
    {
      userType: "bot",
      message: "Hi, fellow coder! 🌟 Welcome to your ZIO adventure with the ZIO Chat Bot. 🚀 Let's master functional Scala together. From referential transparency to concurrent prowess, I've got your back. Ready to dive in? Your questions, my insights – let's conquer ZIO! 💡🤖",
      completed: true
    }
  ]

  function getRandom(arr) {
    const randomIndex = Math.floor(Math.random() * arr.length);
    return arr.splice(randomIndex, 1)[0];
  }

  const { 
    title = 'ByteBrain ChatBot', 
    defaultQuestion = 'Send your message', 
    websocketHost,
    websocketPort,
    websocketEndpoint 
  } = props

  useEffect(() => {
    // Change the title when the component mounts
    const original_title = document.title;
    document.title = title;
    
    // Optionally, you can revert the title when the component unmounts
    return () => {
      document.title = original_title;
    };
  }, []);

  const [question, setQuestion] = React.useState('');
  const [messages, setMessages] = React.useState([getRandom(greetings)]);

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
      const history = messages.map(m => m.message).slice(1);
      const data = {
        "question": question,
        "history": history
      }
      ws.send(JSON.stringify(data));
    };
    ws.onmessage = function (event) {
      const result = JSON.parse(event.data)
      const word = result.token;
      const references = result.references;
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
            references: references,
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
              <ChatMessage key={id} id={"chat" + id} userType={m.userType} text={m.message} references={m.references} highlight={m.completed} />
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