import { ModeToggle } from "@/components/mode-toggle";
import { ThemeProvider } from "@/components/theme-provider";
import { Button, buttonVariants } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import { BrowserRouter, Link, NavLink, Route, Routes } from "react-router-dom";
import { DataTable } from "./app/data-table";
import { ChevronLeft } from "lucide-react";
import moment from 'moment'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";


import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import './App.css';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";



"use client"

import { Check, ChevronsUpDown } from "lucide-react";
import * as React from "react";


import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";




import { cn } from "@/lib/utils"
import { Icons } from "@/components/icons"
import { UserAuthForm } from "@/authentication/components/user-auth-form"


function LoginPage() {
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <Link
        to="/"
        className={cn(
          buttonVariants({ variant: "ghost" }),
          "absolute left-4 top-4 md:left-8 md:top-8"
        )}
      >
        <>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back
        </>
      </Link>
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <Icons.logo className="mx-auto h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">
            Welcome back
          </h1>
          <p className="text-sm text-muted-foreground">
            Enter your email to sign in to your account
          </p>
        </div>
        <UserAuthForm />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link
            to="/signup"
            className="hover:text-brand underline underline-offset-4"
          >
            Don&apos;t have an account? Sign Up
          </Link>
        </p>
      </div>
    </div>
  )
}





const frameworks = [
  {
    value: "cpp",
    label: "CPP",
  },
  {
    value: "go",
    label: "GO",
  },
  {
    value: "java",
    label: "JAVA",
  },
  {
    value: "kotlin",
    label: "KOTLIN",
  },
  {
    value: "js",
    label: "JS",
  },
  {
    value: "ts",
    label: "TS",
  },
  {
    value: "php",
    label: "PHP",
  },
  {
    value: "proto",
    label: "PROTO",
  },
  {
    value: "python",
    label: "PYTHON",
  },
  {
    value: "rst",
    label: "RST",
  },
  {
    value: "ruby",
    label: "RUBY",
  },
  {
    value: "rust",
    label: "RUST",
  },
  {
    value: "scala",
    label: "SCALA",
  },
  {
    value: "swift",
    label: "SWIFT",
  },
  {
    value: "markdown",
    label: "MARKDOWN",
  },
  {
    value: "latex",
    label: "LATEX",
  },
  {
    value: "html",
    label: "HTML",
  },
  {
    value: "sol",
    label: "SOL",
  },
  {
    value: "csharp",
    label: "CSHARP",
  },
];

export function ComboboxDemo() {
  const [open, setOpen] = React.useState(false)
  const [value, setValue] = React.useState("")

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {value
            ? frameworks.find((framework) => framework.value === value)?.label
            : "Select language..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search framework..." />
          <CommandEmpty>No framework found.</CommandEmpty>
          <CommandGroup className="h-52">
            {frameworks.map((framework) => (
              <CommandItem
                key={framework.value}
                value={framework.value}
                onSelect={(currentValue) => {
                  setValue(currentValue === value ? "" : currentValue)
                  setOpen(false)
                }}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    value === framework.value ? "opacity-100" : "opacity-0"
                  )}
                />
                {framework.label}
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  )
}


function Projects() {

  type Project = {
    id: string
    name: string
  }

  const projects: Project[] = [
    {
      id: "1",
      name: "ZIO Ecosystem",
    },
    {
      id: "2",
      name: "Golem"
    },
    {
      id: "3",
      name: "Caliban"
    }
  ]


  const projectsColumns: ColumnDef<Project>[] = [
    {
      accessorKey: "id",
      header: "ID",
    },
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const project = row.original

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
              <DropdownMenuItem>Delete</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <NavLink to="/resources">Manage Resources</NavLink>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      }
    }]


  return (
    <>
      <NavBar />



      <div className="flex items-center justify-between pt-5">

        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">Projects</h2>



        <Dialog>
          <DialogTrigger>
            <Button className="">
              <PlusCircleIcon className="mr-2 h-4 w-4" />
              Create Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create a New Project</DialogTitle>
              <DialogDescription>
                <form>
                  <div className="grid w-full items-center gap-4 pt-10">
                    <div className="flex flex-col space-y-1.5">
                      <Label htmlFor="name" className="font-extrabold pb-2">Name</Label>
                      <Input id="name" placeholder="Name of your project" />
                    </div>
                    <div className="flex flex-col space-y-1.5 pt-4">
                      <Label htmlFor="name" className="font-extrabold pb-2">Description</Label>
                      <Input id="name" placeholder="Description of your project" />
                    </div>
                  </div>

                  <div className="flex flex-row-reverse">
                    <Button className="flex mt-10 justify-items-end">Create</Button>
                  </div>
                </form>


              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>



      </div>

      <div className="container mx-auto py-10">
        <DataTable columns={projectsColumns} data={projects} />
      </div>

    </>
  )
}

function Tables() {

  return (
    <>
      <Collapsible>
        <table border={2}>
          <thead>
            <tr>
              <th>Name-------------------</th>
              <th>Age</th>
              <th>City</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <CollapsibleTrigger>
                <td>John</td>
              </CollapsibleTrigger>
              <td>45</td>
              <td>London</td>
            </tr>
            <CollapsibleContent>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Age</th>
                    <th>City</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Ali</td>
                    <td>35</td>
                    <td>Isfahan</td>
                  </tr>
                </tbody>
              </table>
            </CollapsibleContent>
            <tr>
              <td>Mike</td>
              <td>40</td>
              <td>Manchester</td>
            </tr>
            <tr>
              <td>Steve</td>
              <td>50</td>
              <td>Birmingham</td>
            </tr>
          </tbody>
        </table>
      </Collapsible>

    </>
  )
}


function Resources() {

  type Resource = {
    id: string
    name: string
    type: "Website" | "Webpage" | "Github" | "Youtube"
    status: "Pending" | "Success" | "Failed"
    created_at: string
  }


  const resourcesColumns: ColumnDef<Resource>[] = [
    {
      accessorKey: "id",
      header: "ID",
    },
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      accessorKey: "type",
      header: "Type",
    },
    {
      accessorKey: "status",
      header: "Status",
    },
    {
      accessorKey: "updated_at",
      header: "Last Update",
      cell: ({ row }) => {
        const resource = row.original
        const parsedDate = moment(resource.created_at).format("YYYY-MM-DD mm:ss")

        return parsedDate
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const resource = row.original

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
              <DropdownMenuItem onClick={() => { }} >Delete</DropdownMenuItem>
              <DropdownMenuItem>Renew Ingestion</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Indexed Documents</DropdownMenuItem>
            </DropdownMenuContent>

          </DropdownMenu>
        )
      }
    }
  ]

  const resources: Resource[] = [
    {
      "id": "1",
      "name": "Website 1",
      "type": "Website",
      "status": "Pending",
      "updated_at": "2022-01-01T00:00:00Z"
    },
    {
      "id": "2",
      "name": "Webpage 1",
      "type": "Webpage",
      "status": "Success",
      "updated_at": "2022-01-02T00:00:00Z"
    },
    {
      "id": "3",
      "name": "Github Repo 1",
      "type": "Github",
      "status": "Failed",
      "updated_at": "2022-01-03T00:00:00Z"
    },
    {
      "id": "4",
      "name": "Youtube Video 1",
      "type": "Youtube",
      "status": "Success",
      "updated_at": "2022-01-04T00:00:00Z"
    },
  ]

  return (
    <>

      <NavBar />


      <div className="flex items-center justify-between pt-5">

        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">Data Sources</h2>



        <Dialog>
          <DialogTrigger>
            <Button className="">
              <PlusCircleIcon className="mr-2 h-4 w-4" />
              Add New Data Sources
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="text-2xl">Add New Data Source</DialogTitle>
              <DialogDescription>
                <form>
                  <Tabs defaultValue="website" className="w-[400px] pt-5 pb-5">
                    <TabsList>
                      <TabsTrigger value="website">Website</TabsTrigger>
                      <TabsTrigger value="webpage">Webpage</TabsTrigger>
                      <TabsTrigger value="github">Github</TabsTrigger>
                      <TabsTrigger value="youtube">Youtube</TabsTrigger>
                    </TabsList>
                    <TabsContent value="website" className="pt-3">Crawl a whole website and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="name" className="font-extrabold pb-2">Name</Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col space-y-1.5 pt-4">
                          <Label htmlFor="url" className="font-extrabold pb-2">URL</Label>
                          <Input id="url" placeholder="Website URL" />
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="webpage" className="pt-3">Crawl a url and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="name" className="font-extrabold pb-2">Name</Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col space-y-1.5 pt-4">
                          <Label htmlFor="url" className="font-extrabold pb-2">URL</Label>
                          <Input id="url" placeholder="Webpage URL" />
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="github" className="pt-3">Clone a public repository and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex items-center flex-row pt-1">
                          <Label htmlFor="name" className="font-extrabold w-1/5">Name</Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col pt-1">
                          <Label htmlFor="url" className="font-extrabold pb-2">Clone URL</Label>
                          <Input id="url" placeholder="https://github.com/<namespace>/<project_name>.git" />
                        </div>
                        <div className="flex items-center flex-row pt-2">
                          <Label htmlFor="branch" className="font-extrabold w-1/5">Branch</Label>
                          <Input id="branch" placeholder="main" className="" />
                        </div>
                        <div className="flex items-center justify-between flex-row pt-2">
                          <Label htmlFor="path" className="font-extrabold pb-2 w-1/5">Path</Label>
                          <Input id="path" placeholder="Glob Pattern, e.g. /docs/**/*.md" />
                        </div>
                        <div className="flex items-center justify-between flex-row pt-1">
                          <Label htmlFor="path" className="font-extrabold w-2/5">Language</Label>
                          <ComboboxDemo />
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="youtube" className="pt-3">Fetch Youtube's subtitle and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="name" className="font-extrabold pb-2">Name</Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col space-y-1.5 pt-4">
                          <Label htmlFor="url" className="font-extrabold pb-2">Youtube URL</Label>
                          <Input id="url" placeholder="https://www.youtube.com/watch?v=<video_id>" />
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                  <div className="flex pt-3 pb-3">
                    <Button className="justify-items-center">Create</Button>
                  </div>
                </form>
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>



      </div>

      <div className="container mx-auto py-10">
        <DataTable columns={resourcesColumns} data={resources} />
      </div>

    </>
  )
}



function NavBar() {
  return (
    <div className="flex h-16 items-center justify-between border-b border-b-slate-200 py-4 ">
      <div className="flex space-x-6">
        <Link className="hidden items-center space-x-2 md:flex" to="/projects" >
          <span className="hidden font-bold sm:inline-block">Projects</span>
        </Link>
        <a className="hidden items-center space-x-2 md:flex"
          href="/"
          data-bcup-haslogintext="no"
        >
          <span className="hidden sm:inline-block">Chat Bot</span>
        </a>
        <a className="hidden items-center space-x-2 md:flex"
          href="/"
          data-bcup-haslogintext="no"
        >
          <span className="hidden sm:inline-block">Conversations</span>
        </a>
        <a className="hidden items-center space-x-2 md:flex"
          href="/"
          data-bcup-haslogintext="no"
        >
          <span className="hidden sm:inline-block">Insight</span>
        </a>
      </div>
      <div className="flex space-x-3">
        <ModeToggle />
        <a className="hidden items-center space-x-2 md:flex"
          href="/"
          data-bcup-haslogintext="no"
        >
          <span className="hidden sm:inline-block">Profile</span>
        </a>
      </div>
    </div>
  )
}


function Signup() {

  return (
    <>
      <div className="md:hidden">
        {/* <Image
          src="/examples/authentication-light.png"
          width={1280}
          height={843}
          alt="Authentication"
          className="block dark:hidden"
        />
        <Image
          src="/examples/authentication-dark.png"
          width={1280}
          height={843}
          alt="Authentication"
          className="hidden dark:block"
        /> */}
      </div>
      <div className="container relative hidden h-[800px] flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
        <Link
          to="/login"
          className={cn(
            buttonVariants({ variant: "ghost" }),
            "absolute right-4 top-4 md:right-8 md:top-8"
          )}
        >
          Login
        </Link>
        <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
          <div className="absolute inset-0 bg-zinc-900" />
          <div className="relative z-20 flex items-center text-lg font-medium">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mr-2 h-6 w-6"
            >
              <path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
            </svg>
            Ziverge Inc
          </div>
          <div className="relative z-20 mt-auto">
            <blockquote className="space-y-2">
              <p className="text-lg">
                &ldquo;Our team found ByteBrain AI a game-changer. It’s like a Swiss Army knife for navigating technical documents.
.&rdquo;
              </p>
              <footer className="text-sm">Adam Fraser</footer>
            </blockquote>
          </div>
        </div>
        <div className="lg:p-8">
          <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
            <div className="flex flex-col space-y-2 text-center">
              <h1 className="text-2xl font-semibold tracking-tight">
                Create an account
              </h1>
              <p className="text-sm text-muted-foreground">
                Enter your email below to create your account
              </p>
            </div>
            <UserAuthForm />
            <p className="px-8 text-center text-sm text-muted-foreground">
              By clicking continue, you agree to our{" "}
              <Link
                to="/terms"
                className="underline underline-offset-4 hover:text-primary"
              >
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link
                to="/privacy"
                className="underline underline-offset-4 hover:text-primary"
              >
                Privacy Policy
              </Link>
              .
            </p>
          </div>
        </div>
      </div>
    </>
  )
}

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">

        <BrowserRouter>
          <Routes>
            <Route path="/projects" element={<Projects />} />
            <Route path="/tables" element={<Tables />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </>
  )
}

export default App
