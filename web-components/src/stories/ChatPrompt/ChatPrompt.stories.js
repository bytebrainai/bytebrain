import { ChatPrompt } from './ChatPrompt';

export default {
  title: 'Chat/ChatPrompt',
  component: ChatPrompt,
  tags: ['autodocs'],
  argTypes: {
    backgroundColor: { control: 'color' }
  },
};

export const ZIOChat =  {
  args: {
    title: "ZIO Chat",
    defaultQuestion: "What are the befenits of using ZIO?",
    websocketEndpoint: 'ws://localhost:8081/chat'
  }
}
