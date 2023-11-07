import React, { useState, useEffect } from 'react';
import ThumbsUp from './thumbs-up';
import ThumbsDown from './thumbs-down';
import './FeedbackForm.css';
import Message from './Message';

interface FeedbackFormProps {
  chatHistory: Message[];
  baseHttpUrl: string;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({ chatHistory, baseHttpUrl }) => {
  const [isUseful, setIsUseful] = useState<boolean | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<boolean>(false);

  useEffect(() => {
    setIsUseful(null);
    setFeedbackSubmitted(false);
  }, []);

  const handleSubmit = async (value: boolean) => {
    try {
      if (feedbackSubmitted) {
        return;
      }

      setIsUseful(value);

      const response = await fetch(`${baseHttpUrl}/feedback/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_history: chatHistory,
          is_useful: value,
        }),
      });

      if (response.ok) {
        console.log('Feedback submitted successfully');
        setFeedbackSubmitted(true);
      } else {
        console.error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <form>
      <button
        type="button"
        title="It was helpful to me!"
        className={`feedback-button inline-block ${feedbackSubmitted && !isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(true)}
        disabled={feedbackSubmitted}
      >
        <ThumbsUp />
      </button>
      <button
        type="button"
        title="It didn't help me at all!"
        className={`feedback-button inline-block ${feedbackSubmitted && isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(false)}
        disabled={feedbackSubmitted}
      >
        <ThumbsDown />
      </button>
    </form>
  );
};

export default FeedbackForm;
