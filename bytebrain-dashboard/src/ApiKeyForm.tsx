import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useToast } from "@/components/ui/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFieldArray, useForm } from "react-hook-form";
import * as z from "zod";

import { Input } from "@/components/ui/input";

import "./App.css";
import { Resource, Result, Unauthorized } from "./Projects";
import { cn } from "./lib/utils";

("use client");

function ApiKeyForm({
  project_id,
  setOpen,
  rerender,
  setRerender,
}: {
  project_id: string;
  setOpen: (open: boolean) => void;
  rerender: boolean;
  setRerender: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const { toast } = useToast();

  const apiKeyFormSchema = z.object({
    name: z.string(),
    allowed_domains: z.array(
      z.object({
        value: z
          .string()
          .regex(
            new RegExp("^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(.[A-Za-z]{2,})+$"),
            { message: "Please enter a valid domain" }
          ),
      })
    ),
  });

  const apiKeyForm = useForm<z.infer<typeof apiKeyFormSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(apiKeyFormSchema),
    defaultValues: {
      name: "",
      allowed_domains: [],
    },
  });

  const { fields, append } = useFieldArray({
    name: "allowed_domains",
    control: apiKeyForm.control,
  });

  async function onSubmitForm(values: z.infer<typeof apiKeyFormSchema>) {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      const result = await generateNewApiKey(
        access_token,
        values.name,
        values.allowed_domains.map((v) => v.value),
        project_id
      );
      if (result.value) {
        toast({
          description: "New API Key generated!",
        });
        setOpen(false);
        setRerender(!rerender);
      } else {
        toast({
          description:
            "There was an error creating resource. Please try again!",
        });
      }
    } else {
      window.location.assign("http://localhost:5173/auth/login");
    }
  }

  async function generateNewApiKey(
    access_token: string,
    name: string,
    allowed_domains: string[],
    project_id: string
  ): Promise<Result<Resource, Error>> {
    try {
      const response = await fetch(
        `http://localhost:8081/projects/${project_id}/apikeys`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${access_token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: name,
            allowed_domains: allowed_domains,
          }),
        }
      );
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          window.location.assign("http://localhost:5173/auth/login");
          return { value: null, error: new Unauthorized() };
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }
  }

  return (
    <Form {...apiKeyForm}>
      <form onSubmit={apiKeyForm.handleSubmit(onSubmitForm)}>
        <div className="grid w-full items-center gap-4 pt-5">
          <div className="flex flex-col space-y-1.5">
            <FormField
              control={apiKeyForm.control}
              name="name"
              render={({ field, formState }) => (
                <FormItem>
                  <FormLabel className="font-extrabold pb-2">Name</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="Api Key Name"
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
            <div className="pt-3">
              {fields.map((field, index) => (
                <FormField
                  control={apiKeyForm.control}
                  key={field.id}
                  name={`allowed_domains.${index}.value`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className={cn(index !== 0 && "sr-only")}>
                        <span className="font-extrabold">Allowed Domains</span>
                      </FormLabel>
                      <FormDescription className={cn(index !== 0 && "sr-only")}>
                        Add a domain that you want to allow to use this API key.
                      </FormDescription>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() => append({ value: "" })}
              >
                Add Domain (Optional)
              </Button>
            </div>
            <div className="flex pt-3 pb-3">
              <Button className="justify-items-center">Create</Button>
            </div>
          </div>
        </div>
      </form>
    </Form>
  );
}

export default ApiKeyForm;
