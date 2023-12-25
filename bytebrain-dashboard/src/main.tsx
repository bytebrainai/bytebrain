import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  // Disabled StrictMode because it causes double rendering
  // <React.StrictMode>
  <App />
  // </React.StrictMode>,
);
