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

import { EyeIcon, EyeOffIcon } from "lucide-react";
import React from "react";
import { useState } from "react";

("use client");

const ApiKeyComponent = ({ apiKey }: { apiKey: string }) => {
  const [masked, setMasked] = useState(true);
  const charactersToShow = 30;
  const maskedString =
    "*".repeat(charactersToShow) + apiKey.substring(charactersToShow);

  return (
    <div className="flex flex-row gap-2">
      <pre>{masked ? maskedString : apiKey}</pre>
      <EyeToggle
        defaultValue={!masked}
        onToggle={() => setMasked(!masked)}
      />{" "}
    </div>
  );
};

export default ApiKeyComponent;

const EyeToggle = ({
  defaultValue,
  onToggle,
}: {
  defaultValue: boolean;
  onToggle: () => void;
}) => {
  const [enabled, setEnabled] = React.useState(defaultValue);
  return (
    <>
      {enabled ? (
        <EyeIcon
          className="w-4 h-4"
          onClick={() => {
            setEnabled(false);
            onToggle();
          }}
        />
      ) : (
        <EyeOffIcon
          className="w-4 h-4"
          onClick={() => {
            setEnabled(true);
            onToggle();
          }}
        />
      )}
    </>
  );
};
