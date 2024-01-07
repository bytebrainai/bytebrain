import { ThemeProvider } from "@/components/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import DashboardLayout from "./DashboardLayout";
import LoginPage from "./LoginPage";
import { Projects } from "./Projects";
import { Resources } from "./Resources";
import Signup from "./Signup";
import { Toaster } from "./components/ui/toaster";

("use client");

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DashboardLayout />} >
              <Route path="" element={<Projects />} />
              <Route path="projects" element={<Projects />} />
              <Route path="projects/:project_id/resources" element={<Resources />} />
            </Route>
            <Route path="/auth/signup" element={<Signup />} />
            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth" element={<LoginPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </ThemeProvider>
    </>
  );
}

export default App;
