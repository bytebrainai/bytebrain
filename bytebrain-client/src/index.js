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

import { ChatPrompt } from "@bytebrain.ai/bytebrain-ui";
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import reportWebVitals from "./reportWebVitals";

const root = ReactDOM.createRoot(document.getElementById("root"));
const welcome_messages = [
  "🌟 Greetings from ZIO Chat! 🌟 Have questions about ZIO? Look no further! I'm here to be your ZIO guru. Whether you're a seasoned pro or just starting out, I've got answers tailored just for you. Fire away with your ZIO queries, and I'll hit you back with the best insights I've got. Let's dive into the world of ZIO together!",
  "🔥 Ignite your ZIO journey with ZIO Chat! 🔥 Ready to unravel the intricacies of ZIO? As your trusty sidekick, I'm here to light the way. No matter if you're wandering through functional forests or traversing effectful landscapes, I've got answers to keep you on track. Your ZIO adventure starts here – ask me anything and let's explore together!",
  "Hello! 😊 I'm your ZIO Chat Bot, designed to be your go-to resource for all things ZIO! Whether you're new to this powerful functional effect system or a seasoned pro, I'm here to assist you. ZIO empowers you to build concurrent and resilient applications in Scala, offering referential transparency, composable data types, type-safety, and more. So, go ahead and ask me anything about ZIO – I'm here to provide the answers you need! 🤖",
  "Hi there! 👋 I'm ZIO Chat, your friendly neighborhood ZIO expert. I'm here to help you navigate the world of ZIO. Whether you're a seasoned pro or just starting out, fire away with your ZIO questions. I will hit you back with the best insights I've got. Let's dive into the world of ZIO together!",
  "🎉 Hey there, ZIO aficionado! 🎉 Step into the ZIO wonderland with me as your guide. Whether you're a functional fanatic or just dipping your toes into the ZIO ecosystem, I'm here to make your journey smooth. Got ZIO questions? I've got answers! Let's navigate the ZIO universe together and unlock its infinite possibilities!",
  "Hi, fellow coder! 🌟 Welcome to your ZIO adventure with the ZIO Chat Bot. 🚀 Let's master functional Scala together. From referential transparency to concurrent prowess, I've got your back. Ready to dive in? Your questions, my insights – let's conquer ZIO! 💡🤖",
];

root.render(
  <React.StrictMode>
    <ChatPrompt
      title="ZIO Chat"
      defaultQuestion="Write a question about ZIO!"
      websocketHost=""
      websocketPort="80"
      websocketEndpoint="/chat"
      welcomeMessages={welcome_messages}
      fullScreen={true}
    />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
