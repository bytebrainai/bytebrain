import React from 'react';
import './RelatedQuestions.css';

type QuestionItem = string;

interface RelatedQuestionsProps {
  items?: QuestionItem[];
  setQuestion: React.Dispatch<React.SetStateAction<string>>;
}

export const RelatedQuestions: React.FC<RelatedQuestionsProps> = ({ items, setQuestion }) => {
  return (
    <>
      {items && items.length > 0 ? (
        <div className="text-xs px-4 pt-2 rounded-br-none bg-blue-500 text-white">
          <h3 className="text-xs font-bold">Ask Related Questions:</h3>
          <ol className="list-inside custom-list">
            {items.map((item, index) => (
              <li key={index} className="mr-2">
                <a
                  className="underline text-white text-sm"
                  href="#"
                  onClick={(event) => setQuestion((event.target as HTMLAnchorElement).textContent!)}
                >
                  {item}
                </a>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </>
  );
};

export default RelatedQuestions;
