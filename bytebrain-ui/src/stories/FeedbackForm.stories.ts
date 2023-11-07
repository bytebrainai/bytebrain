import { FeedbackForm } from "./FeedbackForm";

export default {
  title: "Feedback/FeedbackForm",
  component: FeedbackForm,
  tags: ["autodocs"],
};

export const FeedbackFormSample = {
  args: {
    chatHistory: ["User: Hello!", "Bot: Hi there!"],
    baseHttpUrl: 'http://localhost:8081'
  },
};
