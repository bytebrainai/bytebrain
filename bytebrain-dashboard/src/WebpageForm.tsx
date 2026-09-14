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
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useToast } from "@/components/ui/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { Input } from "@/components/ui/input";

import "./App.css";
import { Resource, Result, Unauthorized } from "./Projects";

("use client");


function WebpageForm({ project_id, updateProject, setOpen }: { project_id: string, updateProject: () => void, setOpen: (open: boolean) => void }) {
  const { toast } = useToast();

  const webpageFormSchema = z.object({
    name: z.string(),
    url: z.string().url({ message: "Invalid URL" }),
  });

  const webpageForm = useForm<z.infer<typeof webpageFormSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(webpageFormSchema),
    defaultValues: {
      name: "",
      url: "",
    },
  });

  async function createWebpageResource(access_token: string, name: string, url: string, project_id: string): Promise<Result<Resource, Error>> {
    try {
      const response = await fetch(`http://localhost:8081/resources/webpage`, {
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

  async function onSubmitWebpageForm(values: z.infer<typeof webpageFormSchema>) {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      const result = await createWebpageResource(access_token, values.name, values.url, project_id);
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


  return (
    <Form {...webpageForm}>
      <form onSubmit={webpageForm.handleSubmit(onSubmitWebpageForm)}>
        <div className="grid w-full items-center gap-4 pt-5">
          <div className="flex flex-col space-y-1.5">
            <FormField
              control={webpageForm.control}
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
              control={webpageForm.control}
              name="url"
              render={({ field, formState }) => (
                <FormItem className="pt-4">
                  <FormLabel className="font-extrabold pb-2">URL</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="Website URL"
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
  )


}

export default WebpageForm;