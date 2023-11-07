import React from 'react';

export type ReferenceItem = {
  page_url: string;
  page_title: string;
};

interface ReferencesProps {
  items?: ReferenceItem[];
}

export const References: React.FC<ReferencesProps> = ({ items }) => {
  return (
    <>
      {items && items.length > 0 ? (
        <div className="text-xs px-4 py-2 rounded-b-lg rounded-br-none bg-blue-500 text-white">
          <h3 className="text-xs font-bold">Discover Related Sources:</h3>
          <ol className="flex flex-wrap list-inside pl-0">
            {items.map((item, index) => (
              <li key={index} className="mr-2">
                <a className="underline text-white text-sm" href={item.page_url}>{item.page_title}</a>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </>
  );
};

export default References;
