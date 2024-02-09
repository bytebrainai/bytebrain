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

import React, { useState } from 'react';
import PopupChatWindow from './PopupChatWindow';

interface ChatAppProps {
  websocketHost?: string;
  websocketPort?: string;
  websocketEndpoint: string;
  apikey: string;
}

const ChatApp: React.FC<ChatAppProps> = (props) => {
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
        apikey={props.apikey}
      />
    </>
  );
};

export default ChatApp;
