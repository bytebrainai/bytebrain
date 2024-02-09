/**
 * Copyright 2023-2024 ByteBrain AI
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
      <div className="flex items-center justify-between pt-5 pl-8 pr-8">
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
