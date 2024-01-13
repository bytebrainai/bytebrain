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
