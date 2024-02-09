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