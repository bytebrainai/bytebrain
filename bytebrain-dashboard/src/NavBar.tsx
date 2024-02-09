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

import { ModeToggle } from "@/components/mode-toggle";
import { Link } from "react-router-dom";
import { cn } from "./lib/utils";

import "./App.css";
import Profile from "./Profile";
import { ProjectSwitcher, ProjectSwitcherProps } from "./project-switcher";
import { Separator } from "@/components/ui/separator"

("use client");

export function NavBar({ projects: projects, currentProjectId: currentProjectId }: ProjectSwitcherProps) {
  return (
    <>
      <div className="flex h-16 items-center justify-between py-4 ">
        <div className="flex flex-row">
          <Link className="hidden items-center space-x-2 md:flex" to="/projects">
            <span className="hidden font-bold sm:inline-block">Home</span>
          </Link>
          <div className={cn("flex h-[52px] items-center justify-center", 'px-2')}>
            <ProjectSwitcher projects={projects} currentProjectId={currentProjectId} />
          </div>
        </div>
        <div className="flex space-x-6">
          {/* <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <span className="hidden sm:inline-block">Chat Bot</span>
          </a>
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <span className="hidden sm:inline-block">Conversations</span>
          </a>
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <span className="hidden sm:inline-block">Insight</span>
          </a> */}
        </div>
        <div className="flex space-x-3">
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <span className="hidden sm:inline-block">Blog</span>
          </a>
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <span className="hidden sm:inline-block">Docs</span>
          </a>
          <ModeToggle />
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
            data-bcup-haslogintext="no"
          >
            <Profile />
          </a>
        </div>
      </div>
      <Separator />
    </>
  );
}

export default NavBar;