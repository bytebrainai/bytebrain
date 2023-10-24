import React, { useState } from 'react';
import { useEffect } from 'react';
import ThumbsUp from './thumbs-up';
import ThumbsDown from './thumbs-down';

export const FeedbackForm = (props) => {
  const [chatHistory, setChatHistory] = useState(props.chatHistory);
  const [isUseful, setIsUseful] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    setChatHistory(props.chatHistory);
    console.log("chatHistory", chatHistory);
  }, [props]);

  const handleSubmit = async (value) => {
    try {
      if (feedbackSubmitted) {
        return;
      }

      setIsUseful(value);

      const response = await fetch(props.baseHttpUrl + '/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_history: chatHistory,
          is_useful: value
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
        title='It was helpful to me!'
        className={`inline-block ${feedbackSubmitted && !isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(true)} disabled={feedbackSubmitted}>
        <ThumbsUp />
      </button>
      <button
        type="button"
        title="It didn't help me at all!"
        className={`inline-block ${feedbackSubmitted && isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(false)} disabled={feedbackSubmitted}>
        <ThumbsDown />
      </button>
    </form>
  );
};

export default FeedbackForm;
