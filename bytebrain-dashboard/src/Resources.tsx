import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import moment from "moment";
import { useState } from "react";
import { DataTable } from "./app/data-table";

import { useNavigate, useParams } from 'react-router-dom';

import "./App.css";
import { NavBar } from "./NavBar";
import { Project, Resource, Result, Unauthorized } from "./Projects";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

("use client");

import * as React from "react";
import NewDataSourceDialog from "./NewDataSourceDialog";

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













  const [open, setOpen] = useState(false);

  return (
    <>
      <NavBar projects={projects} currentProjectId={project_id} />

      <h1 className="h-11 text-4xl font-medium leading-tight sm:text-4xl sm:leading-normal">{project.name}</h1>
      <p className="text-sm text-muted-foreground pt-3 pb-3">{project.description}</p>

      <Tabs defaultValue="data-sources" className="pt-5 pb-5" onValueChange={(v) => {
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
            <NewDataSourceDialog open={open} setOpen={setOpen} project_id={project.id} updateProject={updateProject} />
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

