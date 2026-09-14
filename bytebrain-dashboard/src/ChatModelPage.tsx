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

import { Tabs, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import React from "react";
import { useToast } from "./components/ui/use-toast";

import { MaxLengthSelector } from "./components/maxlength-selector";
import { ModelSelector } from "./components/model-selector";
import { TemperatureSelector } from "./components/temperature-selector";
import { TemplateSave } from "./components/template-save";
import { TopPSelector } from "./components/top-p-selector";
import { models } from "./data/models";

export type ChatModel = {
  id: string;
  project_id: string;
  name: string;
  prompt: string;
  created_at: Date;
};

export default function ChatModelPage({
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

  const template = `
      You are expert in providing detailed answers about ZIO library and it's ecosystem projects.
    Given the piece of information inside the CONTEXT section and also your base knowledge, prepare an answer for the USER's QUESTION. 
    Only answer the question, if the question is related to the CONTEXT section.
    Before returning the FINAL ANSWER, refactor your answer in your mind with REFACTOR RULES. 
    If you don't know the answer, please say this exactly: I don't have enough information to answer your question about ...
    
    After answering the USER'S QUESTION, you "must" write 3 other related questions that a user can ask about the current topic. Questions should be in following format:
   
    Related Questions:
      1. Question 1
      2. Question 2
    
    Before listing related questions, engage the user with a warming follow-up message.
    ----- 
    REFACTOR RULES: 
    If USER asked you to write code, you shouldn't use ZIO 1.x APIs in your generated response, instead you should only 
    use ZIO 2.x APIs.
    To make sure that your code is compatible with ZIO 2.x API, use the following migration table from ZIO 1.x to ZIO 2.x
    
    | ZIO 1.x API | ZIO 2.x API |
    +-------------+-------------+
    | putStrLn | Console.printLine |
    | getStrLn | Console.readLine |
    | zio.App | zio.ZIOAppDefault |
    | extends zio.ZIOApp | extends ZIOAppDefault |
    | extends App | extends ZIOAppDefault |
    | def run(args: List[String]) | def run =  |
    | ZIO.effect | ZIO.attempt |
    | ZIO.effectTotal | ZIO.succeed |
    | console.putStrLn | Console.printLine |
    | override def run(args: List[String]) | def run =  |
    
    Remove any of following packages from import section: ["zio.console.Console"] 
    Add backticks for inline codes and three backticks for code blocks.
    ------
    CONTEXT:
    
    {context}
    ------
    USER'S QUESTION: {question}
    ------
    FINAL ANSWER (THE ANSWER + RELATED QUESTIONS):

  `;

  return (
    <>
      <div className="hidden h-full flex-col md:flex">
        <div className="flex items-center justify-between pt-5 pl-8 pr-8">
          <h2 className="h-11 text-3xl font-medium leading-tight sm:text-3xl sm:leading-normal">
            Customize Chat Model
          </h2>
          <div className="ml-auto flex space-x-2 sm:justify-end">
            <TemplateSave />
          </div>
        </div>
        {/* <Separator /> */}
        <Tabs defaultValue="complete" className="flex-1">
          <div className="container h-full py-6">
            <div className="grid h-full items-stretch gap-6 md:grid-cols-[1fr_200px]">
              <div className="hidden flex-col space-y-4 sm:flex md:order-2">
                <ModelSelector models={models} />
                <TemperatureSelector defaultValue={[0.56]} />
                <MaxLengthSelector defaultValue={[256]} />
                <TopPSelector defaultValue={[0.9]} />
              </div>
              <div className="md:order-1">
                <TabsContent value="complete" className="mt-0 border-0 p-0">
                  <div className="flex h-full flex-col space-y-4">
                    <Textarea
                      placeholder={template}
                      className="min-h-[200px] flex-1 p-4 md:min-h-[200px] lg:min-h-[300px]"
                    />
                  </div>
                </TabsContent>
              </div>
            </div>
          </div>
        </Tabs>
      </div>
    </>
  );
}
