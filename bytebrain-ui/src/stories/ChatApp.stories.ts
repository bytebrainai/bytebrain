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
    projectId: "<project_id>"
  },
};

export const ChatAppProduction = {
  args: {
    websocketHost: "chat.zio.dev",
    websocketPort: "80",
    websocketEndpoint: "/chat",
    projectId: "<project_id>"
  },
};
