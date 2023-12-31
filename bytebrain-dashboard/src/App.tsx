import { ThemeProvider } from "@/components/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthApp } from "./AuthApp";
import { LoginPage } from "./LoginPage";
import { Projects } from "./Projects";
import { Resources } from "./Resources";
import { RootApp } from "./RootApp";
import { Signup } from "./Signup";
import { Toaster } from "./components/ui/toaster";

("use client");

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <BrowserRouter>
          <Routes>
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:project_id/resources" element={<Resources />}/>
            <Route path="/auth/signup" element={<Signup />} />
            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth" element={<LoginPage />} />
            <Route path="/" element={<Projects />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </ThemeProvider>
    </>
  );
}

export default App;
