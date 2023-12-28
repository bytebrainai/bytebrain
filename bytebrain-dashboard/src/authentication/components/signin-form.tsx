"use client";

import React, { useEffect } from "react";

import { Icons } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { getAccessToken, loginWithGithub } from "./signup-form";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

interface SigninFormProps extends React.HTMLAttributes<HTMLDivElement> {}

const formSchema = z.object({
  username: z.string().email({ message: "Invalid email address." }),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters long." })
    .max(20, { message: "Password must be at most 20 characters long." }),
});

export function SigninForm({ className, ...props }: SigninFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  async function onSubmitForm(values: z.infer<typeof formSchema>) {
    const access_token = await login(values.username, values.password);

    if (access_token.success && localStorage.getItem("accessToken") == null) {
      console.log(access_token);
      localStorage.setItem("accessToken", access_token.data);
      toast({
        description: "Successfully logged-in",
      });
      setTimeout(() => {
        window.location.assign("http://localhost:5173");
      }, 2000);
    } else if (!access_token.success && access_token.error === "Unauthorized") {
      toast({
        description: "Username or password is incorrect!",
      });
    } else {
      toast({
        description: "There was an error logging in. Please try again.",
      });
    }
  }

  const { toast } = useToast();

  useEffect(() => {
    const fetchAndStoreAccessToken = async () => {
      const queryString = window.location.search;
      const urlParams = new URLSearchParams(queryString);
      const githubCodeParam = urlParams.get("code");

      if (githubCodeParam && localStorage.getItem("accessToken") == null) {
        const access_token = await getAccessToken(githubCodeParam);
        if (access_token.success) {
          localStorage.setItem("accessToken", access_token.data);
          toast({
            description: "Successfully logged-in",
          });

          setTimeout(() => {
            window.location.assign("http://localhost:5173");
          }, 2000);
        } else {
          toast({
            description: "Failed to log-in",
          });
        }
      }
    };

    fetchAndStoreAccessToken();

    if (localStorage.getItem("accessToken")) {
      window.location.assign("http://localhost:5173");
    }
  }, []);

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmitForm)}>
          <div className="grid gap-2">
            <div className="grid gap-1">
              <FormField
                control={form.control}
                name="username"
                render={({ field, formState }) => (
                  <FormItem>
                    <FormLabel className="sr-only">Email</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Email Address"
                        autoCapitalize="none"
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
                name="password"
                render={({ field, formState }) => (
                  <FormItem>
                    <FormLabel className="sr-only">Password</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Password"
                        type="password"
                        autoCapitalize="none"
                        autoComplete="true"
                        autoCorrect="off"
                        onClick={() => {
                          console.log(field);
                        }}
                        disabled={formState.isSubmitting}
                      ></Input>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <Button type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting && (
                <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
              )}
              Login with Email
            </Button>
          </div>
        </form>
      </Form>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            continue with
          </span>
        </div>
      </div>
      <Button
        variant="outline"
        type="button"
        disabled={form.formState.isSubmitting}
        onClick={loginWithGithub}
      >
        {form.formState.isSubmitting ? (
          <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Icons.gitHub className="mr-2 h-4 w-4" />
        )}{" "}
        Github
      </Button>
    </div>
  );
}

async function login(
  username: string,
  password: string
): Promise<
  { success: true; data: string } | { success: false; error: string }
> {
  const url = "http://127.0.0.1:8081/auth/access_token";

  const headers = {
    Accept: "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
  };

  const data = {
    username: username,
    password: password,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: new URLSearchParams(data),
    });

    if (response.status === 401) {
      return { success: false, error: "Unauthorized" };
    }
    const responseData = await response.json();
    return { success: true, data: responseData.access_token };
  } catch (error) {
    return { success: false, error: JSON.stringify(error) };
  }
}
