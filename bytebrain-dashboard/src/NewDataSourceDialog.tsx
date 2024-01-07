import { Button } from "@/components/ui/button";
import { PlusCircleIcon } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import "./App.css";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

import GitHubForm from "./GitHubForm";
import WebpageForm from "./WebpageForm";
import WebsiteForm from "./WebsiteForm";
import YoutubeForm from "./YoutubeForm";

("use client");


function NewDataSourceDialog(
  { open, setOpen, project_id, updateProject }:
    { open: boolean, setOpen: (open: boolean) => void, project_id: string, updateProject: () => void }) {
  return (
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
                <WebsiteForm project_id={project_id} updateProject={updateProject} setOpen={setOpen} />
              </TabsContent>
              <TabsContent value="webpage" className="pt-3">
                Crawl a url and ingest it.
                <WebpageForm project_id={project_id} updateProject={updateProject} setOpen={setOpen} />
              </TabsContent>
              <TabsContent value="github" className="pt-3">
                Clone a public repository and ingest it.
                <GitHubForm project_id={project_id} updateProject={updateProject} setOpen={setOpen} />
              </TabsContent>
              <TabsContent value="youtube" className="pt-3">
                Fetch Youtube's subtitle and ingest it.
                <YoutubeForm project_id={project_id} updateProject={updateProject} setOpen={setOpen} />
              </TabsContent>
            </Tabs>
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  )
}

export default NewDataSourceDialog;