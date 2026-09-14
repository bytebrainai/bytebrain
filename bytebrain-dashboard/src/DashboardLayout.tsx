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

import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import "./App.css";
import NavBar from "./NavBar";
import { Project, Result, Unauthorized } from "./Projects";
import { useToast } from "./components/ui/use-toast";

("use client");

function DashboardLayout() {
  const { toast } = useToast();
  const [rerender, setRerender] = React.useState(false);

  const [projects, setProjects] = useState<Project[]>([]);

  async function getProjects(
    access_token: string
  ): Promise<Result<Project[], Error>> {
    try {
      const response = await fetch("http://localhost:8081/projects", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          return { value: null, error: new Unauthorized() };
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }
  }

  function updateProjects() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getProjects(access_token).then((result) => {
        if (result.value) {
          setProjects(result.value);
        } else {
          toast({
            description:
              "There was an error fetching projects. Please try again!",
          });
        }
      });
    } else {
      window.location.assign("http://localhost:5173/auth/login");
    }
  }

  const project_id = localStorage.getItem("currentProjectId") || "";

  React.useEffect(() => {
    updateProjects();
  }, [rerender]);

  return (
    <>
      <header>
        <NavBar projects={projects} currentProjectId={project_id} />
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}

export default DashboardLayout;
