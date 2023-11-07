import React, { useState } from 'react';
import PopupChatWindow from './PopupChatWindow';

interface IChatAppProps {
  websocketHost?: string;
  websocketPort?: string;
  websocketEndpoint: string;
}

const ChatApp: React.FC<IChatAppProps> = (props) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const close = () => setIsOpen(false); // Function to close the chat window
  const open = () => setIsOpen(true); // Function to open the chat window

  return (
    <>
      <button
        id="chat-button"
        className="fixed border-0 font-sans text-xl bg-orange-400 rounded-tl-md text-black px-3 py-2 hover:scale-95 transition text-ms bottom-0 right-0"
        onClick={open}
      >
        ZIO Chat!
      </button>
      <PopupChatWindow
        onClose={close}
        visible={isOpen}
        websocketHost={props.websocketHost}
        websocketPort={props.websocketPort}
        websocketEndpoint={props.websocketEndpoint}
      />
    </>
  );
};

export default ChatApp;
