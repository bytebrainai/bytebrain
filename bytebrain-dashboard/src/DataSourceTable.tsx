import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import moment from "moment";
import { DataTable } from "./app/data-table";


import "./App.css";
import { Resource, Result, Unauthorized } from "./Projects";

("use client");


function DataSourceTable({ resources, rerender, setRerender }: { resources: Resource[], rerender: boolean, setRerender: (rerender: boolean) => void }) {
  const { toast } = useToast();


  const resourcesColumns: ColumnDef<Resource>[] = [
    {
      accessorKey: "resource_name",
      header: "Name",
    },
    {
      accessorKey: "resource_type",
      header: "Type",
      cell: (info) => {
        const value = (info.getValue() as string)
        return value.charAt(0).toUpperCase() + value.slice(1)
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: (info) => {
        const value = (info.getValue() as string)
        return value.charAt(0).toUpperCase() + value.slice(1)
      }
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
              <DropdownMenuItem onClick={() => {
                deleteResource(resource.resource_id);
                setRerender(!rerender);
              }}>Delete</DropdownMenuItem>
              <DropdownMenuItem>Renew Ingestion</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Indexed Documents</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  async function deleteResource(id: string): Promise<Result<boolean, Error>> {

    const access_token = localStorage.getItem("accessToken");

    try {
      const response = await fetch(`http://localhost:8081/resources/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })
      if (response.status === 204) {
        toast({
          description: "Successfully deleted the resource",
        });
        return { value: true, error: null };
      } else if (response.status === 401) {
        window.location.assign(
          "http://localhost:5173/auth/login"
        );
        return { value: false, error: new Unauthorized() }
      } else if (response.status === 404) {
        toast({
          description: "Specified resouce not found for deletion!",
        });
      }
      toast({
        description: "There was an error deleting the resource. Please try again!",
      });
      return { value: false, error: Error(response.statusText) };
    } catch (error) {
      toast({
        description: "There was an error deleting the resource. Please try again!",
      });
      return { value: false, error: Error(JSON.stringify(error)) };
    }

  }

  return (
    <DataTable columns={resourcesColumns} data={resources} />
  )

}

export default DataSourceTable;