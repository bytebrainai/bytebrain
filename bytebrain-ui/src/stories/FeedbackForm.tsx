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
        className={`dark:bg-[#242526] bg-gray-100 feedback-button inline-block ${feedbackSubmitted && !isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(true)}
        disabled={feedbackSubmitted}
      >
        <ThumbsUp />
      </button>
      <button
        type="button"
        title="It didn't help me at all!"
        className={`dark:bg-[#242526] bg-gray-100 feedback-button inline-block ${feedbackSubmitted && isUseful ? 'hidden' : ''}`}
        onClick={() => handleSubmit(false)}
        disabled={feedbackSubmitted}
      >
        <ThumbsDown />
      </button>
    </form>
  );
};

export default FeedbackForm;
