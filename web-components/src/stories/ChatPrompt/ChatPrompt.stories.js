import { ChatPrompt } from './ChatPrompt';

export default {
  title: 'Chat/ChatPrompt',
  component: ChatPrompt,
  tags: ['autodocs'],
  argTypes: {
    backgroundColor: { control: 'color' },
  },
};

export const Simple = {
  args: {
    primary: true,
    label: 'Button',
  },
};
