import React from "react";
import ApiKeyTable from "./ApiKeyTable";
import NewApiKeyDialog from "./NewApiKeyDialog";
import { useToast } from "./components/ui/use-toast";

export type ApiKey = {
  name: string;
  created_at: string;
  apikey: string;
  allowed_domains: string[];
};

export default function ApiKeyPage({
  open,
  setOpen,
  project_id,
}: {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  project_id: string;
}) {
  const { toast } = useToast();
  const [rerender, setRerender] = React.useState(false);

  return (
    <>
      <div className="flex items-center justify-between pt-5">
        <h2 className="h-11 text-3xl font-medium leading-tight sm:text-3xl sm:leading-normal">
          Api Key
        </h2>
        <NewApiKeyDialog
          open={open}
          setOpen={setOpen}
          project_id={project_id}
          rerender={rerender}
          setRerender={setRerender}
        />
      </div>
      <div className="container mx-auto py-10">
        <ApiKeyTable
          project_id={project_id}
          rerender={rerender}
          setRerender={setRerender}
          open={open}
          setOpen={setOpen}
        />
      </div>
    </>
  );
}
