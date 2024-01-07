import { Button } from "@/components/ui/button";
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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useToast } from "@/components/ui/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import moment from "moment";
import { useState } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";
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
import { useNavigate, useParams } from 'react-router-dom';

import "./App.css";
import { NavBar } from "./NavBar";
import { Project, Resource, Result, Unauthorized } from "./Projects";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

("use client");

import * as React from "react";


import GitHubForm from "./GitHubForm";
import WebpageForm from "./WebpageForm";
import WebsiteForm from "./WebsiteForm";


export function Resources(props: any) {
  const navigate = useNavigate();
  const [rerender, setRerender] = React.useState(false);
  const [project, setProject] = React.useState<Project>({
    id: "",
    name: "",
    user_id: "",
    resources: [],
    created_at: "",
    description: ""
  });
  const [projects, setProjects] = useState<Project[]>([]);
  const { project_id } = useParams();

  async function getProject(access_token: string): Promise<Result<Project, Error>> {
    try {
      const response = await fetch(`http://localhost:8081/projects/${project_id}`, {
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

  const { toast } = useToast();

  function updateProject() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getProject(access_token).then((result) => {
        if (result.value) {
          setProject(result.value);
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

  React.useEffect(() => {
    updateProject();
    updateProjects();
  }, [rerender]);


  async function deleteResource(id: string): Promise<Result<boolean, Error>> {

    const access_token = localStorage.getItem("accessToken");

    try {
      const response = await fetch(`http://localhost:8081/resources/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })
      if (response.status === 204) {
        toast({
          description: "Successfully deleted the resource",
        });
        return { value: true, error: null };
      } else if (response.status === 401) {
        window.location.assign(
          "http://localhost:5173/auth/login"
        );
        return { value: false, error: new Unauthorized() }
      } else if (response.status === 404) {
        toast({
          description: "Specified resouce not found for deletion!",
        });
      }
      toast({
        description: "There was an error deleting the resource. Please try again!",
      });
      return { value: false, error: Error(response.statusText) };
    } catch (error) {
      toast({
        description: "There was an error deleting the resource. Please try again!",
      });
      return { value: false, error: Error(JSON.stringify(error)) };
    }

  }



  const resourcesColumns: ColumnDef<Resource>[] = [
    {
      accessorKey: "resource_name",
      header: "Name",
    },
    {
      accessorKey: "resource_type",
      header: "Type",
      cell: (info) => {
        const value = (info.getValue() as string)
        return value.charAt(0).toUpperCase() + value.slice(1)
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: (info) => {
        const value = (info.getValue() as string)
        return value.charAt(0).toUpperCase() + value.slice(1)
      }
    },
    {
      accessorKey: "updated_at",
      header: "Last Update",
      cell: ({ row }) => {
        const resource = row.original;
        const parsedDate = moment(moment(resource.updated_at)).fromNow();

        return parsedDate;
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const resource = row.original;

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
              <DropdownMenuItem onClick={() => {
                deleteResource(resource.resource_id);
                setRerender(!rerender);
              }}>Delete</DropdownMenuItem>
              <DropdownMenuItem>Renew Ingestion</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Indexed Documents</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];







  const youtubeFormSchema = z.object({
    name: z.string(),
    url: z.string().url({ message: "Invalid URL" }),
  });

  const youtubeForm = useForm<z.infer<typeof youtubeFormSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(youtubeFormSchema),
    defaultValues: {
      name: "",
      url: "",
    },
  });







  async function createYoutubeResource(
    access_token: string,
    name: string,
    url: string,
    project_id: string): Promise<Result<Resource, Error>> {
    try {
      const response = await fetch(`http://localhost:8081/resources/youtube`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          url: url,
          project_id: project_id,
        })
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

  async function onSubmitYoutubeForm(values: z.infer<typeof youtubeFormSchema>) {
    console.log(values)
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      const result = await createYoutubeResource(access_token, values.name, values.url, project.id);
      if (result.value) {
        toast({
          description: "Successfully created resource",
        });
        updateProject();
        setOpen(false);
      } else {
        toast({
          description: "There was an error creating resource. Please try again!",
        });
      }
    } else {
      window.location.assign(
        "http://localhost:5173/auth/login"
      );
    }
  }

  const [open, setOpen] = useState(false);

  return (
    <>
      <NavBar projects={projects} currentProjectId={project_id} />

      <h1 className="h-11 text-4xl font-medium leading-tight sm:text-4xl sm:leading-normal">{project.name}</h1>
      <p className="text-sm text-muted-foreground pt-3 pb-3">{project.description}</p>

      <Tabs defaultValue="data-sources" className="pt-5 pb-5" onValueChange={(v) => {
        console.log(v);
        navigate(`/projects/${project_id}/${v}`, { replace: false })
      }}>
        <TabsList>
          <TabsTrigger value="data-sources">Data Sources</TabsTrigger>
          <TabsTrigger value="chatbot">ChatBot</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="data-sources" className="pt-3">
          <div className="flex items-center justify-between pt-5">
            <h2 className="h-11 text-3xl font-medium leading-tight sm:text-3xl sm:leading-normal">Data Sources</h2>
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger>
                <Button className="">
                  <PlusCircleIcon className="mr-2 h-4 w-4" />
                  Add New Data Sources
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-2xl">
                    Add New Data Source
                  </DialogTitle>
                  <DialogDescription>
                    <Tabs defaultValue="website" className="w-[400px] pt-5 pb-5">
                      <TabsList>
                        <TabsTrigger value="website">Website</TabsTrigger>
                        <TabsTrigger value="webpage">Webpage</TabsTrigger>
                        <TabsTrigger value="github">GitHub</TabsTrigger>
                        <TabsTrigger value="youtube">Youtube</TabsTrigger>
                      </TabsList>
                      <TabsContent value="website" className="pt-3">
                        Crawl the entire website and ingest it.
                        <WebsiteForm project_id={project.id} updateProject={updateProject} setOpen={setOpen} />
                      </TabsContent>
                      <TabsContent value="webpage" className="pt-3">
                        Crawl a url and ingest it.
                        <WebpageForm project_id={project.id} updateProject={updateProject} setOpen={setOpen} />
                      </TabsContent>
                      <TabsContent value="github" className="pt-3">
                        Clone a public repository and ingest it.
                        <GitHubForm project_id={project.id} updateProject={updateProject} setOpen={setOpen} />
                      </TabsContent>
                      <TabsContent value="youtube" className="pt-3">
                        Fetch Youtube's subtitle and ingest it.
                        <Form {...youtubeForm}>
                          <form onSubmit={youtubeForm.handleSubmit(onSubmitYoutubeForm)}>
                            <div className="grid w-full items-center gap-4 pt-5">
                              <div className="flex flex-col space-y-1.5">
                                <FormField
                                  control={youtubeForm.control}
                                  name="name"
                                  render={({ field, formState }) => (
                                    <FormItem>
                                      <FormLabel className="font-extrabold pb-2">Name</FormLabel>
                                      <FormControl>
                                        <Input
                                          {...field}
                                          placeholder="Resource Name"
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
                                  control={youtubeForm.control}
                                  name="url"
                                  render={({ field, formState }) => (
                                    <FormItem>
                                      <FormLabel className="font-extrabold pb-2">Youtube Url</FormLabel>
                                      <FormControl>
                                        <Input
                                          {...field}
                                          placeholder="https://www.youtube.com/watch?v=<video_id>"
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
                                <div className="flex pt-3 pb-3">
                                  <Button type="submit" className="justify-items-center">Create</Button>
                                </div>
                              </div>
                            </div>
                          </form>
                        </Form>
                      </TabsContent>
                    </Tabs>
                  </DialogDescription>
                </DialogHeader>
              </DialogContent>
            </Dialog>
          </div>
          <div className="container mx-auto py-10">
            <DataTable columns={resourcesColumns} data={project ? project.resources : []} />
          </div>
        </TabsContent>
        <TabsContent value="settings" className="pt-3">
        </TabsContent>
      </Tabs>
    </>
  );
}

export default Resources;

