import { ModeToggle } from "@/components/mode-toggle";
import { Link } from "react-router-dom";

import "./App.css";
import Profile from "./Profile";

("use client");

export function NavBar() {
  return (
    <div className="flex h-16 items-center justify-between border-b border-b-slate-200 py-4 ">
      <div className="flex space-x-6">
        <Link className="hidden items-center space-x-2 md:flex" to="/projects">
          <span className="hidden font-bold sm:inline-block">Projects</span>
        </Link>
        <a
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
        </a>
      </div>
      <div className="flex space-x-3">
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
  );
}

export default NavBar;