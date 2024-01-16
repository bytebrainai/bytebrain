import { useToast } from "@/components/ui/use-toast";
import { useState } from "react";

import { useParams } from "react-router-dom";

import "./App.css";
import { Project, Result, Unauthorized } from "./Projects";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

("use client");

import * as React from "react";
import ApiKeyPage from "./ApiKeyPage";
import DataSourceTable from "./DataSourceTable";
import NewDataSourceDialog from "./NewDataSourceDialog";
import ChatModelPage from "./ChatModelPage";

export function Resources(props: any) {
  const [open, setOpen] = useState(false);
  const [rerender, setRerender] = React.useState(false);

  const [project, setProject] = React.useState<Project>({
    id: "",
    name: "",
    user_id: "",
    resources: [],
    created_at: "",
    description: "",
  });
  const [projects, setProjects] = useState<Project[]>([]);
  const { project_id } = useParams();
  localStorage.setItem("currentProjectId", project_id || "");

  async function getProject(
    access_token: string
  ): Promise<Result<Project, Error>> {
    try {
      const response = await fetch(
        `http://localhost:8081/projects/${project_id}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        }
      );
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

  const { toast } = useToast();

  function updateProject() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getProject(access_token).then((result) => {
        if (result.value) {
          setProject(result.value);
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

  React.useEffect(() => {
    updateProject();
    updateProjects();
  }, [rerender]);

  return (
    <>
      <h1 className="h-11 text-4xl font-medium leading-tight sm:text-4xl sm:leading-normal">
        {project.name}
      </h1>
      <p className="text-sm text-muted-foreground pt-3 pb-3">
        {project.description}
      </p>

      <Tabs defaultValue="data-sources" className="pt-5 pb-5">
        <TabsList>
          <TabsTrigger value="data-sources">Data Sources</TabsTrigger>
          <TabsTrigger value="api-key">API Key</TabsTrigger>
          <TabsTrigger value="chat-model">Chat Model</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="data-sources" className="pt-3">
          <div className="flex items-center justify-between pt-5 pl-8 pr-8">
            <h2 className="h-11 text-3xl font-medium leading-tight sm:text-3xl sm:leading-normal">
              Data Sources
            </h2>
            <NewDataSourceDialog
              open={open}
              setOpen={setOpen}
              project_id={project.id}
              updateProject={updateProject}
            />
          </div>
          <div className="container mx-auto py-10">
            <DataSourceTable
              resources={project.resources}
              rerender={rerender}
              setRerender={setRerender}
            />
          </div>
        </TabsContent>
        <TabsContent value="api-key" className="pt-3">
          <ApiKeyPage open={open} setOpen={setOpen} project_id={project.id} />
        </TabsContent>
        <TabsContent value="chat-model" className="pt-3">
          <ChatModelPage open={open} setOpen={setOpen} project_id={project.id} />
        </TabsContent>
        <TabsContent value="settings" className="pt-3  pl-8 pr-8">
          <h2 className="h-11 text-3xl font-medium leading-tight sm:text-3xl sm:leading-normal">
            Data Sources
          </h2>
          <SettingForm />
        </TabsContent>
      </Tabs>
    </>
  );
}

export default Resources;

function SettingForm() {
  return (
    <>
      <p className="text-sm text-muted-foreground">
        This is how others will see you on the site.
      </p>
    </>
  );
}
