import ChatApp from "./ChatApp";

export default {
  title: "Chat/ChatApp",
  component: ChatApp,
  tags: ["autodocs"],
};

export const ChatAppDevelopment = {
  args: {
    websocketHost: "localhost",
    websocketPort: "8081",
    websocketEndpoint: "/chat",
    apikey: "<apikey>"
  },
};

export const ChatAppProduction = {
  args: {
    websocketHost: "chat.zio.dev",
    websocketPort: "80",
    websocketEndpoint: "/chat",
    apikey: "<apikey>"
  },
};
