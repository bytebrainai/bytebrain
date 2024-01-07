"use client"

import * as React from "react"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

export interface ProjectSwitcherProps {
  projects: {
    id: string
    name: string
  }[],
  currentProjectId: string | undefined
}

export function ProjectSwitcher({
  projects: projects,
  currentProjectId: currentProjectId
}: ProjectSwitcherProps) {
  const [selectedProject, setSelectedProject] = React.useState<string>(
    currentProjectId ? currentProjectId : ""
  )


  return (
    <>
      <Select defaultValue={selectedProject} onValueChange={(value) => {
        window.location.assign(
          `http://localhost:5173/projects/${value}/resources`
        );
      }
      }>
        <SelectTrigger
          className={cn(
            "flex items-center gap-2 [&>span]:line-clamp-1 [&>span]:flex [&>span]:w-full [&>span]:items-center [&>span]:gap-1 [&>span]:truncate [&_svg]:h-4 [&_svg]:w-4 [&_svg]:shrink-0"
          )}
          aria-label="Select project"
        >
          <SelectValue placeholder="Select a project">
            <span className={cn("ml-2")}>
              {
                projects.find((project) => project.id === selectedProject)
                  ?.name
              }
            </span>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {projects.map((project) => (
            <SelectItem key={project.id} value={project.id}>
              <div className="flex items-center gap-3 [&_svg]:h-4 [&_svg]:w-4 [&_svg]:shrink-0 [&_svg]:text-foreground">
                {project.name}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select >
    </>
  )
}
