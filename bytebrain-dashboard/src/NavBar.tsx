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