import { Button } from "@/components/ui/button";
import { PlusCircleIcon } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import "./App.css";

import ApiKeyForm from "./ApiKeyForm";

("use client");

function NewApiKeyDialog({
  open,
  setOpen,
  project_id,
  rerender,
  setRerender,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  project_id: string;
  rerender: boolean;
  setRerender: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger>
        <Button className="">
          <PlusCircleIcon className="mr-2 h-4 w-4" />
          Generate New Key
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl">Generate New Key</DialogTitle>
          <DialogDescription>
            To generate a new key, please enter a name and allowed domains.
            <ApiKeyForm
              project_id={project_id}
              setOpen={setOpen}
              rerender={rerender}
              setRerender={setRerender}
            />
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}

export default NewApiKeyDialog;
