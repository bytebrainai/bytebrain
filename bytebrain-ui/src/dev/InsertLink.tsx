import React, { useState } from 'react';
import './InsertLink.css'

export const InsertLink = (props) => {
  const [textareaValue, setTextareaValue] = useState('');

  const handleClick = (event) => {
    const content = event.target.textContent;
    setTextareaValue((prevState) => content);
  };

  return (
    <div>
      <a href="#" onClick={handleClick}>Insert content</a>
      <textarea value={textareaValue} />
    </div>
  );
};

export default InsertLink;


