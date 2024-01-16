export interface PromptTemplate {
  id: string
  name: string
  description: string
  strengths?: string
}

export const models: PromptTemplate[] = [
  {
    id: "c305f976-8e38-42b1-9fb7-d21b2e34f0da",
    name: "Retrieval Question/Answering",
    description:
      "Most capable GPT-3 model. Can do any task the other models can do, often with higher quality, longer output and better instruction-following. Also supports inserting completions within text.",
    strengths:
      "Complex intent, cause and effect, creative generation, search, summarization for audience",
  },
]
