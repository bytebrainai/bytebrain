import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import moment from "moment";
import { useState } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { DataTable } from "./app/data-table";

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
import { useLocation, useParams } from 'react-router-dom';

import "./App.css";
import { NavBar } from "./NavBar";
import { Project, Resource, Result, Unauthorized } from "./Projects";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

("use client");

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

import { cn } from "@/lib/utils";

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
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState("");

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
                  setValue(currentValue === value ? "" : currentValue);
                  setOpen(false);
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
  );
}

export function Resources(props: any) {
  const location = useLocation();
  const [project, setProject] = React.useState<Project>({
    id: "",
    name: "",
    user_id: "",
    resources: [],
    created_at: "",
  });
  const { project_id } = useParams();

  async function getProject(access_token: string): Promise<Result<Project, Error>> {
    try {
      const response = await fetch(`http://localhost:8081/projects/${project_id}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
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

  const { toast } = useToast();

  function updateProject() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getProject(access_token).then((result) => {
        if (result.value) {
          setProject(result.value);
        } else {
          toast({
            description: "There was an error fetching projects. Please try again!",
          });
        }
      });
    } else {
      window.location.assign(
        "http://localhost:5173/auth/login"
      );

    }

  }

  React.useEffect(() => {
    updateProject();
  }, []);

  const resourcesColumns: ColumnDef<Resource>[] = [
    {
      accessorKey: "resource_id",
      header: "ID",
    },
    {
      accessorKey: "resource_name",
      header: "Name",
    },
    {
      accessorKey: "resource_type",
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
        const resource = row.original;
        const parsedDate = moment(moment(resource.updated_at)).fromNow();

        return parsedDate;
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const resource = row.original;

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
              <DropdownMenuItem onClick={() => { }}>Delete</DropdownMenuItem>
              <DropdownMenuItem>Renew Ingestion</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Indexed Documents</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];


  const websiteFormSchema = z.object({
    name: z.string(),
    url: z.string().url({ message: "Invalid URL" }),
  });

  const websiteForm = useForm<z.infer<typeof websiteFormSchema>>({
    mode: "onSubmit",
    resolver: zodResolver(websiteFormSchema),
    defaultValues: {
      name: "",
      url: "",
    },
  });


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

  async function createWebsiteResource(access_token: string, name: string, url: string, project_id: string): Promise<Result<Resource, Error>> {
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

  async function onSubmitWebsiteForm(values: z.infer<typeof websiteFormSchema>) {
    console.log(values)
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      const result = await createWebsiteResource(access_token, values.name, values.url, project.id);
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
      const result = await createWebpageResource(access_token, values.name, values.url, project.id);
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



  const [open, setOpen] = useState(false);

  return (
    <>
      <NavBar />

      <div className="flex items-center justify-between pt-5">
        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">Data Sources</h2>

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
                    <Form {...websiteForm}>
                      <form onSubmit={websiteForm.handleSubmit(onSubmitWebsiteForm)}>
                        <div className="grid w-full items-center gap-4 pt-5">
                          <div className="flex flex-col space-y-1.5">
                            <FormField
                              control={websiteForm.control}
                              name="name"
                              render={({ field, formState }) => (
                                <FormItem>
                                  <FormLabel className="sr-only">Resource Name</FormLabel>
                                  <FormControl>
                                    <>
                                      <Label htmlFor="name" className="font-extrabold pb-2">
                                        Name
                                      </Label>
                                      <Input
                                        {...field}
                                        placeholder="Resource Name"
                                        autoCapitalize="none"
                                        autoComplete="true"
                                        autoCorrect="off"
                                        disabled={formState.isSubmitting}
                                      />
                                    </>
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <FormField
                              control={websiteForm.control}
                              name="url"
                              render={({ field, formState }) => (
                                <FormItem className="pt-4">
                                  <FormLabel className="sr-only">Website URL</FormLabel>
                                  <FormControl>
                                    <>
                                      <Label htmlFor="name" className="font-extrabold pb-2">
                                        URL
                                      </Label>
                                      <Input
                                        {...field}
                                        placeholder="Website URL"
                                        autoCapitalize="none"
                                        autoComplete="true"
                                        autoCorrect="off"
                                        disabled={formState.isSubmitting}
                                      />
                                    </>
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <div className="flex pt-3 pb-3">
                              <Button className="justify-items-center">Create</Button>
                            </div>
                          </div>
                        </div>
                      </form>
                    </Form>
                  </TabsContent>
                  <TabsContent value="webpage" className="pt-3">
                    Crawl a url and ingest it.
                    <Form {...webpageForm}>
                      <form onSubmit={webpageForm.handleSubmit(onSubmitWebpageForm)}>
                        <div className="grid w-full items-center gap-4 pt-5">
                          <div className="flex flex-col space-y-1.5">
                            <FormField
                              control={webpageForm.control}
                              name="name"
                              render={({ field, formState }) => (
                                <FormItem>
                                  <FormLabel className="sr-only">Resource Name</FormLabel>
                                  <FormControl>
                                    <>
                                      <Label htmlFor="name" className="font-extrabold pb-2">
                                        Name
                                      </Label>
                                      <Input
                                        {...field}
                                        placeholder="Resource Name"
                                        autoCapitalize="none"
                                        autoComplete="true"
                                        autoCorrect="off"
                                        disabled={formState.isSubmitting}
                                      />
                                    </>
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
                                  <FormLabel className="sr-only">Website URL</FormLabel>
                                  <FormControl>
                                    <>
                                      <Label htmlFor="name" className="font-extrabold pb-2">
                                        URL
                                      </Label>
                                      <Input
                                        {...field}
                                        placeholder="Website URL"
                                        autoCapitalize="none"
                                        autoComplete="true"
                                        autoCorrect="off"
                                        disabled={formState.isSubmitting}
                                      />
                                    </>
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <div className="flex pt-3 pb-3">
                              <Button className="justify-items-center">Create</Button>
                            </div>
                          </div>
                        </div>
                      </form>
                    </Form>
                  </TabsContent>
                  <TabsContent value="github" className="pt-3">
                    Clone a public repository and ingest it.
                    <div className="grid w-full items-center gap-4 pt-5">
                      <div className="flex items-center flex-row pt-1">
                        <Label
                          htmlFor="name"
                          className="font-extrabold w-1/5"
                        >
                          Name
                        </Label>
                        <Input id="name" placeholder="Name of Data Source" />
                      </div>
                      <div className="flex flex-col pt-1">
                        <Label htmlFor="url" className="font-extrabold pb-2">
                          Clone URL
                        </Label>
                        <Input
                          id="url"
                          placeholder="https://github.com/<namespace>/<project_name>.git"
                        />
                      </div>
                      <div className="flex items-center flex-row pt-2">
                        <Label
                          htmlFor="branch"
                          className="font-extrabold w-1/5"
                        >
                          Branch
                        </Label>
                        <Input id="branch" placeholder="main" className="" />
                      </div>
                      <div className="flex items-center justify-between flex-row pt-2">
                        <Label
                          htmlFor="path"
                          className="font-extrabold pb-2 w-1/5"
                        >
                          Path
                        </Label>
                        <Input
                          id="path"
                          placeholder="Glob Pattern, e.g. /docs/**/*.md"
                        />
                      </div>
                      <div className="flex items-center justify-between flex-row pt-1">
                        <Label
                          htmlFor="path"
                          className="font-extrabold w-2/5"
                        >
                          Language
                        </Label>
                        <ComboboxDemo />
                      </div>
                    </div>
                  </TabsContent>
                  <TabsContent value="youtube" className="pt-3">
                    Fetch Youtube's subtitle and ingest it.



                    <div className="grid w-full items-center gap-4 pt-5">
                      <div className="flex items-center flex-row pt-1">
                        <Label
                          htmlFor="name"
                          className="font-extrabold w-1/5"
                        >
                          Name
                        </Label>
                        <Input id="name" placeholder="Name of Data Source" />
                      </div>
                      <div className="flex flex-col pt-1">
                        <Label htmlFor="url" className="font-extrabold pb-2">
                          Clone URL
                        </Label>
                        <Input
                          id="url"
                          placeholder="https://github.com/<namespace>/<project_name>.git"
                        />
                      </div>
                      <div className="flex items-center flex-row pt-2">
                        <Label
                          htmlFor="branch"
                          className="font-extrabold w-1/5"
                        >
                          Branch
                        </Label>
                        <Input id="branch" placeholder="main" className="" />
                      </div>
                      <div className="flex items-center justify-between flex-row pt-2">
                        <Label
                          htmlFor="path"
                          className="font-extrabold pb-2 w-1/5"
                        >
                          Path
                        </Label>
                        <Input
                          id="path"
                          placeholder="Glob Pattern, e.g. /docs/**/*.md"
                        />
                      </div>
                      <div className="flex items-center justify-between flex-row pt-1">
                        <Label
                          htmlFor="path"
                          className="font-extrabold w-2/5"
                        >
                          Language
                        </Label>
                        <ComboboxDemo />
                      </div>
                    </div>





                    <div className="grid w-full items-center gap-4 pt-5">
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="name" className="font-extrabold pb-2">
                          Name
                        </Label>
                        <Input id="name" placeholder="Name of Data Source" />
                      </div>
                      <div className="flex flex-col space-y-1.5 pt-4">
                        <Label htmlFor="url" className="font-extrabold pb-2">
                          Youtube URL
                        </Label>
                        <Input
                          id="url"
                          placeholder="https://www.youtube.com/watch?v=<video_id>"
                        />
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      </div>

      <div className="container mx-auto py-10">
        <DataTable columns={resourcesColumns} data={project ? project.resources : []} />
      </div>
    </>
  );
}

export default Resources;