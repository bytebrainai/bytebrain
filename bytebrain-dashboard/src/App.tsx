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
