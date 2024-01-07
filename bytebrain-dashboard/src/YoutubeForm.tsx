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


function YoutubeForm({ project_id, updateProject, setOpen }: { project_id: string, updateProject: () => void, setOpen: (open: boolean) => void }) {

  const { toast } = useToast();

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
      const result = await createYoutubeResource(access_token, values.name, values.url, project_id);
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
  )
}

export default YoutubeForm;