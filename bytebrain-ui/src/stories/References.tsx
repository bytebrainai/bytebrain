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
                <a className="underline text-white text-sm hover:text-black" href={item.page_url}>{item.page_title}</a>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </>
  );
};

export default References;
