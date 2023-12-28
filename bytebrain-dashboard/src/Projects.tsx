import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import { NavLink } from "react-router-dom";
import { DataTable } from "./app/data-table";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NavBar } from "./NavBar";  

import "./App.css";

("use client");

export function Projects() {
  type Project = {
    id: string;
    name: string;
  };

  const projects: Project[] = [
    {
      id: "1",
      name: "ZIO Ecosystem",
    },
    {
      id: "2",
      name: "Golem",
    },
    {
      id: "3",
      name: "Caliban",
    },
  ];

  const projectsColumns: ColumnDef<Project>[] = [
    {
      accessorKey: "id",
      header: "ID",
    },
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const project = row.original;

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open Menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem>Delete</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <NavLink to="/resources">Manage Resources</NavLink>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  return (
    <>
      <NavBar />
      <div className="flex items-center justify-between pt-5">
        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">
          Projects
        </h2>

        <Dialog>
          <DialogTrigger>
            <Button className="">
              <PlusCircleIcon className="mr-2 h-4 w-4" />
              Create Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create a New Project</DialogTitle>
              <DialogDescription>
                <form>
                  <div className="grid w-full items-center gap-4 pt-10">
                    <div className="flex flex-col space-y-1.5">
                      <Label htmlFor="name" className="font-extrabold pb-2">
                        Name
                      </Label>
                      <Input id="name" placeholder="Name of your project" />
                    </div>
                    <div className="flex flex-col space-y-1.5 pt-4">
                      <Label htmlFor="name" className="font-extrabold pb-2">
                        Description
                      </Label>
                      <Input
                        id="name"
                        placeholder="Description of your project"
                      />
                    </div>
                  </div>

                  <div className="flex flex-row-reverse">
                    <Button className="flex mt-10 justify-items-end">
                      Create
                    </Button>
                  </div>
                </form>
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      </div>

      <div className="container mx-auto py-10">
        <DataTable columns={projectsColumns} data={projects} />
      </div>
    </>
  );
}

export default Projects;