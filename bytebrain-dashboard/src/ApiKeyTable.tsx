import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { ColumnDef } from "@tanstack/react-table";
import { CopyIcon, MoreHorizontal } from "lucide-react";
import moment from "moment";
import { DataTable } from "./app/data-table";

import React from "react";
import ApiKeyComponent from "./ApiKeyComponent";
import "./App.css";
import { Result, Unauthorized } from "./Projects";

("use client");

function ApiKeyTable({
  project_id,
  rerender,
  setRerender,
  open,
  setOpen,
}: {
  project_id: string;
  rerender: boolean;
  setRerender: React.Dispatch<React.SetStateAction<boolean>>;
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [apiKeys, setApiKeys] = React.useState<ApiKey[]>([]);

  React.useEffect(() => {
    updateApiKeys();
  }, [rerender]);

  async function getApiKeys(
    access_token: string,
    project_id: string
  ): Promise<Result<ApiKey[], Error>> {
    try {
      const response = await fetch(
        `http://localhost:8081/projects/${project_id}/apikeys/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        }
      );
      if (response.ok) {
        const responseData = await response.json();
        return { value: responseData, error: null };
      } else {
        if (response.status === 401) {
          return { value: null, error: new Unauthorized() };
        }
        return { value: null, error: Error(response.statusText) };
      }
    } catch (error) {
      return { value: null, error: Error(JSON.stringify(error)) };
    }
  }

  function updateApiKeys() {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      getApiKeys(access_token, project_id).then((result) => {
        if (result.value) {
          setApiKeys(result.value);
        } else {
          toast({
            description:
              "There was an error fetching projects. Please try again!",
          });
        }
      });
    } else {
      window.location.assign("http://localhost:5173/auth/login");
    }
  }

  async function deleteApiKey(apikey: string): Promise<Result<boolean, Error>> {
    const access_token = localStorage.getItem("accessToken");

    try {
      const response = await fetch(
        `http://localhost:8081/projects/${project_id}/apikeys/${apikey}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        }
      );
      if (response.status === 204) {
        toast({
          description: "Successfully deleted the API Key",
        });
        return { value: true, error: null };
      } else if (response.status === 401) {
        window.location.assign("http://localhost:5173/auth/login");
        return { value: false, error: new Unauthorized() };
      } else if (response.status === 404) {
        toast({
          description: "Specified API Key not found for deletion!",
        });
      }
      toast({
        description:
          "There was an error deleting the API Key. Please try again!",
      });
      return { value: false, error: Error(response.statusText) };
    } catch (error) {
      toast({
        description:
          "There was an error deleting the API Key. Please try again!",
      });
      return { value: false, error: Error(JSON.stringify(error)) };
    }
  }

  type ApiKey = {
    name: string;
    created_at: string;
    apikey: string;
    allowed_domains: string[];
  };

  const { toast } = useToast();

  const apiKeyColumns: ColumnDef<ApiKey>[] = [
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      accessorKey: "apikey",
      header: "Key",
      cell: ({ row }) => {
        return (
          <>
            <div className="flex flex-row space-x-3">
              <ApiKeyComponent apiKey={row.original.apikey} />
              <CopyIcon className="w-4 h-4" onClick={
                () => {
                  navigator.clipboard.writeText(row.original.apikey);
                  toast({
                    description: "Copied API Key to clipboard!",
                  });
                }
              }/>
            </div>
          </>
        );
      },
    },
    {
      accessorKey: "allowed_domains",
      header: "Allowed Domains",
    },
    {
      accessorKey: "created_at",
      header: "Creation date",
      cell: ({ row }) => {
        const apiKey = row.original;
        const parsedDate = moment(moment(apiKey.created_at)).fromNow();
        return parsedDate;
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const obj = row.original;

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
              <DropdownMenuItem
                onClick={() => {
                  deleteApiKey(obj.apikey);
                  setRerender(!rerender);
                }}
              >
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  return (
    <>
      <DataTable columns={apiKeyColumns} data={apiKeys} />
    </>
  );
}

export default ApiKeyTable;
