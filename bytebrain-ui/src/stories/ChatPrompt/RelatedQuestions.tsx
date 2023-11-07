import React from 'react';
import './ChatPrompt.css'
import './RelatedQuestions.css'

function RelatedQuestions(props) {
  return (
    <> {props.items !== undefined && props.items.length > 0 ? (
      <div className="text-xs px-4 pt-2 rounded-br-none bg-blue-500 text-white">
        <h3 className='text-xs font-bold'>Ask Related Questions:</h3>
        <ol className="list-inside custom-list">
          {
            props.items.map((item, index) => (
              <li key={index} className="mr-2">
                <a className="underline text-white text-sm" href='#' onClick={(event) => { props.setQuestion((event.target as HTMLAnchorElement).textContent) }}>{item}</a>
              </li>
            ))
          }</ol>
      </div>) : null}
    </>
  )
}

export default RelatedQuestions;