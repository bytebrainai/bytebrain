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

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";


interface SignupFormProps extends React.HTMLAttributes<HTMLDivElement> { }

const CLIENT_ID = "c9345d9e244bb69e4c59";

const formSchema = z.object({
  full_name: z.string()
    .min(3, { message: "Full name must be at least 3 characters long." })
    .max(20, { message: "Full name must be at most 50 characters long." })
    .regex(/^[A-Za-z]+(?: [A-Za-z]+)*$/, { message: "Full name must only contain alphabets." }),
  username: z.string().email({ message: "Invalid email address." }),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters long." })
    .max(20, { message: "Password must be at most 20 characters long." }),
});


export function loginWithGithub(): void {
  window.location.assign(
    "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID
  );
}

export function SignupForm({ className, ...props }: SignupFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });
  const { toast } = useToast();



  async function onSubmitForm(values: z.infer<typeof formSchema>) {

    const access_token: Result<string> = await signup(
      values.username,
      values.password,
      values.full_name
    );

    if (access_token.success && localStorage.getItem("accessToken") == null) {
      localStorage.setItem("accessToken", access_token.data);
      toast({
        description: "There was an error signing up. Please try again!"
      });
      setTimeout(() => {
        window.location.assign("http://localhost:5173");
      }, 2000);
    } else if (!access_token.success && access_token.error === 'UserAlreadyExists') {
      toast({
        description: "User already exists!",
      });
    } else {
      toast({
        description: "There was an error signing up. Please try again!"
      });
    }

  }

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
            description: "Successfully signed-up",
          });

          setTimeout(() => {
            window.location.assign("http://localhost:5173");
          }, 2000);
        } else {
          toast({
            description: "Failed to sign-up",
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
                name="full_name"
                render={({ field, formState }) => (
                  <FormItem>
                    <FormLabel className="sr-only">Password</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Full Name"
                        autoCapitalize="none"
                        autoComplete="true"
                        autoCorrect="off"
                        disabled={formState.isSubmitting}
                      ></Input>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

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
            <Button disabled={form.formState.isSubmitting} >
              {form.formState.isLoading && (
                <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
              )}
              Sign-up with Email
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

export async function getAccessToken(githubCodeParam: string) {
  const url =
    "http://localhost:8081/auth/github/access_token?code=" + githubCodeParam;

  try {
    const response = await fetch(url, { method: "GET" });
    const responseData = await response.json();
    return { success: true, data: responseData.access_token };
  } catch (error) {
    return { success: false, error: error };
  }
}

// Define a custom type for success
export type Success<T> = {
  success: true;
  data: T;
};

// Define a custom type for failure
export type Failure<T> = {
  success: false;
  error: T;
};

// Define a union type for both success and failure
export type Result<T> = Success<T> | Failure<T>;

export async function signup(
  username: string,
  password: string,
  full_name: string
): Promise<Result<string>> {
  const url = "http://127.0.0.1:8081/auth/signup";

  const headers = {
    Accept: "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
  };

  const data = {
    username: username,
    password: password,
    full_name: full_name,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: new URLSearchParams(data),
    });

    if (response.status === 409) {
      return { success: false, error: "UserAlreadyExists" };
    }

    const responseData = await response.json();
    return { success: true, data: responseData.access_token };
  } catch (error) {
    return { success: false, error: JSON.stringify(error) };
  }
}
