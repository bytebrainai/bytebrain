"use client";

import React, { useEffect } from "react";

import { Icons } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";

interface SignupFormProps extends React.HTMLAttributes<HTMLDivElement> { }

const CLIENT_ID = "c9345d9e244bb69e4c59";

export function loginWithGithub(): void {
  window.location.assign(
    "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID
  );
}

export function SignupForm({ className, ...props }: SignupFormProps) {
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [formData, setFormData] = React.useState({
    username: "",
    password: "",
    full_name: "",
  });
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

  async function handleSignupSubmittion() {
    const access_token: Result<string> = await signup(
      formData.username,
      formData.password,
      formData.full_name
    );

    if (access_token.success && localStorage.getItem("accessToken") == null) {
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

  async function onSubmit(event: React.SyntheticEvent) {
    event.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
    }, 3000);
  }

  const handleChange = (e: any) => {
    console.log(e.target.id, e.target.value);
    const { id, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={onSubmit}>
        <div className="grid gap-2">
          <div className="grid gap-1">
            <Label className="sr-only" htmlFor="full_name">
              Full Name
            </Label>
            <Input
              id="full_name"
              placeholder="Full Name"
              type="full_name"
              value={formData.full_name}
              autoCapitalize="none"
              autoComplete="full_name"
              autoCorrect="off"
              disabled={isLoading}
              onChange={handleChange}
            />
            <Label className="sr-only" htmlFor="email">
              Email
            </Label>
            <Input
              id="username"
              placeholder="Email Address"
              type="email"
              value={formData.username}
              autoCapitalize="none"
              // autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
              onChange={handleChange}
            />
            <Label className="sr-only" htmlFor="password">
              Password
            </Label>
            <Input
              id="password"
              placeholder="Password"
              type="password"
              value={formData.password}
              autoCapitalize="none"
              autoCorrect="off"
              disabled={isLoading}
              onChange={handleChange}
            />
          </div>
          <Button disabled={isLoading} onClick={handleSignupSubmittion}>
            {isLoading && (
              <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
            )}
            Sign-up with Email
          </Button>
        </div>
      </form>
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
        disabled={isLoading}
        onClick={loginWithGithub}
      >
        {isLoading ? (
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
export type Failure = {
  success: false;
  error: any;
};

// Define a union type for both success and failure
export type Result<T> = Success<T> | Failure;

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
    const responseData = await response.json();
    return { success: true, data: responseData.access_token };
  } catch (error) {
    return { success: false, error: error };
  }
}
