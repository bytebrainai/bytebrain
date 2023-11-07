import React, { useState } from 'react';

function ParentComponent() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <ChildComponent count={count} setCount={setCount} />
    </div>
  );
}

export default ParentComponent;


function ChildComponent({ count, setCount }) {
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Increment Count</button>
    </div>
  );
};
