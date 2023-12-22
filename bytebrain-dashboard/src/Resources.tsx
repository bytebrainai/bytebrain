import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, PlusCircleIcon } from "lucide-react";
import moment from "moment";
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

import "./App.css";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { NavBar } from "./NavBar";

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

export function Resources() {
  type Resource = {
    id: string;
    name: string;
    type: "Website" | "Webpage" | "Github" | "Youtube";
    status: "Pending" | "Success" | "Failed";
    updated_at: string;
  };

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
        const resource = row.original;
        const parsedDate = moment(resource.updated_at).format(
          "YYYY-MM-DD mm:ss"
        );

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
              <DropdownMenuItem onClick={() => {}}>Delete</DropdownMenuItem>
              <DropdownMenuItem>Renew Ingestion</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Indexed Documents</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  const resources: Resource[] = [
    {
      id: "1",
      name: "Website 1",
      type: "Website",
      status: "Pending",
      updated_at: "2022-01-01T00:00:00Z",
    },
    {
      id: "2",
      name: "Webpage 1",
      type: "Webpage",
      status: "Success",
      updated_at: "2022-01-02T00:00:00Z",
    },
    {
      id: "3",
      name: "Github Repo 1",
      type: "Github",
      status: "Failed",
      updated_at: "2022-01-03T00:00:00Z",
    },
    {
      id: "4",
      name: "Youtube Video 1",
      type: "Youtube",
      status: "Success",
      updated_at: "2022-01-04T00:00:00Z",
    },
  ];

  return (
    <>
      <NavBar />

      <div className="flex items-center justify-between pt-5">
        <h2 className="h-11 text-2xl font-medium leading-tight sm:text-4xl sm:leading-normal">
          Data Sources
        </h2>

        <Dialog>
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
                <form>
                  <Tabs defaultValue="website" className="w-[400px] pt-5 pb-5">
                    <TabsList>
                      <TabsTrigger value="website">Website</TabsTrigger>
                      <TabsTrigger value="webpage">Webpage</TabsTrigger>
                      <TabsTrigger value="github">Github</TabsTrigger>
                      <TabsTrigger value="youtube">Youtube</TabsTrigger>
                    </TabsList>
                    <TabsContent value="website" className="pt-3">
                      Crawl a whole website and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="name" className="font-extrabold pb-2">
                            Name
                          </Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col space-y-1.5 pt-4">
                          <Label htmlFor="url" className="font-extrabold pb-2">
                            URL
                          </Label>
                          <Input id="url" placeholder="Website URL" />
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="webpage" className="pt-3">
                      Crawl a url and ingest it.
                      <div className="grid w-full items-center gap-4 pt-5">
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="name" className="font-extrabold pb-2">
                            Name
                          </Label>
                          <Input id="name" placeholder="Name of Data Source" />
                        </div>
                        <div className="flex flex-col space-y-1.5 pt-4">
                          <Label htmlFor="url" className="font-extrabold pb-2">
                            URL
                          </Label>
                          <Input id="url" placeholder="Webpage URL" />
                        </div>
                      </div>
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
  );
}

export default Resources;