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

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Form,
  FormControl,
  FormField, FormItem, FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import moment from "moment";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { NavLink } from "react-router-dom";
import * as z from "zod";
import { NavBar } from "./NavBar";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import "./App.css";

("use client");

export function Projects() {
  const [open, setOpen] = useState(false);

  const formSchema = z.object({
    name: z.string()
      .min(3, { message: "Project name must be at least 3 characters long." })
      .max(50, { message: "Project name must be at most 50 characters long." }),
    description: z.string().optional()
  });

  const form = useForm<z.infer<typeof formSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
    },
  });


  const [projects, setProjects] = useState<Project[]>([]);


  async function onSubmitForm(data: z.infer<typeof formSchema>) {
    const project = await createProject(data.name, data.description);
    if (project.value) {
      setProjects([...projects, project.value]);
      setOpen(false);
      toast({
        description: "New project successfully created!",
      });
    } else {
      toast({
        description: "There was an error creating project. Please try again!",
      });
    }
  }

  async function getProjects(access_token: string): Promise<Result<Project[], Error>> {
    try {
      const response = await fetch("http://localhost:8081/projects", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          return { value: null, error: new Unauthorized() }
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }
  }

  async function deleteProject(id: string): Promise<Result<Project[], Error>> {

    const access_token = localStorage.getItem("accessToken");

    try {
      const response = await fetch(`http://localhost:8081/projects/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          return { value: null, error: new Unauthorized() }
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }

  }

  async function createProject(name: string, description: string | undefined): Promise<Result<Project, Error>> {

    const access_token = localStorage.getItem("accessToken");

    const headers = {
      Accept: "application/json",
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access_token}`,
    };

    const data = {
      name: name,
      description: description,
    };

    try {
      const response = await fetch("http://localhost:8081/projects", {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
      })
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          return { value: null, error: new Unauthorized() }
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }
  }

  const { toast } = useToast();


  function updateProjects() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getProjects(access_token).then((result) => {
        if (result.value) {
          setProjects(result.value);
        } else {
          toast({
            description: "There was an error fetching projects. Please try again!",
          });
        }
      });
    } else {
      window.location.assign(
        "http://localhost:5173/auth/login"
      );

    }

  }

  useEffect(() => {
    updateProjects();
  }, []);


  return (
    <>
      <div className="flex items-center justify-between pt-5">
        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">
          Projects
        </h2>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger>
            <Button className="">
              <PlusCircleIcon className="mr-2 h-4 w-4" />
              Create Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create a New Project</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmitForm)}>
                <div className="grid w-full items-center gap-4 pt-10">
                  <div className="flex flex-col space-y-1.5">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field, formState }) => (
                        <FormItem>
                          <FormLabel className="font-extrabold pb-2">Name</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Project Name"
                              autoCapitalize="none"
                              autoComplete="true"
                              autoCorrect="off"
                              disabled={formState.isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="description"
                      render={({ field, formState }) => (
                        <FormItem>
                          <div className="flex flex-col space-y-1.5 pt-4">
                            <FormLabel className="font-extrabold pb-2">Description</FormLabel>
                            <FormControl>
                              <Input
                                {...field}
                                placeholder="Project Description"
                                autoCapitalize="none"
                                autoComplete="true"
                                autoCorrect="off"
                                disabled={formState.isSubmitting}
                              />
                            </FormControl>
                            <FormMessage />
                          </div>
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                <div className="flex flex-row-reverse">
                  <Button className="flex mt-10 justify-items-end">
                    Create
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex flex-wrap justify-start gap-2 pt-10">
        {projects.map((project) => (
          <Card className="w-[380px]">
            <CardHeader>
              <div className="flex flex-row place-content-between">
                <CardTitle> {project.name}</CardTitle>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <span className="sr-only">Open Menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuItem onClick={() => {
                      deleteProject(project.id);
                      updateProjects();
                    }}>Delete</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                      <NavLink to={"/projects/" + project.id + "/resources/"}>Manage Resources</NavLink>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              <CardDescription>Created {moment(project.created_at).fromNow()}</CardDescription>
            </CardHeader>
            <CardContent>
              <p>{project.description}</p>
            </CardContent>
          </Card>
        ))
        }
      </div>
    </>
  );
}

export default Projects;

export enum ResourceType {
  Website = "website",
  Webpage = "webpage",
  Youtube = "youtube",
  GitHub = "github",
}

export enum ResourceStatus {
  Pending = "pending",
  Loading = "loading",
  Indexing = "indexing",
  Finished = "finished",
}

export type Resource = {
  resource_id: string,
  resource_name: string,
  resource_type: ResourceType,
  project_id: string,
  metadata: string,
  status: ResourceStatus,
  created_at: string,
  updated_at: string,
}

export type Project = {
  id: string;
  name: string;
  user_id: string,
  resources: Resource[],
  created_at: string,
  description: string,
};

export interface Result<T, E> {
  value: T | null;
  error: E | null;
}

export class Unauthorized extends Error {
  constructor() {
    super('Invalid username or password');
  }
}