import { NextApiRequest, NextApiResponse } from "next";
import { Chroma } from "langchain/vectorstores/chroma";
import { GoogleGenerativeAIEmbeddings } from "langchain/embeddings";
import { ChatGoogleGenerativeAI } from "langchain/llms/google_palm";

// Define the directory where the vector index is stored
const persistDirectory = "../vector_index_storage"; // Ensure this matches your Chroma persist directory

// Define the embedding and model API keys
const GOOGLE_API_KEY = "AIzaSyCosxAPjrz73sWCDQKSbKvqITMwqcezYhQ";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ message: "Method not allowed" });
    }

    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ message: "Message is required" });
    }

    // Load the persisted vector index
    const embeddings = new GoogleGenerativeAIEmbeddings({
      model: "models/embedding-001",
      google_api_key: GOOGLE_API_KEY,
    });

    const vectorIndex = await Chroma.fromExistingIndex(
      persistDirectory,
      embeddings
    );

    // Retrieve relevant documents
    const relevantDocs = await vectorIndex.invoke(message);

    if (!relevantDocs.length) {
      return res.status(200).json({
        response:
          "No relevant context found. Please rephrase or try another question.",
      });
    }

    // Combine context from retrieved documents
    const retrievedContext = relevantDocs
      .map((doc: { page_content: any }) => doc.page_content)
      .join("\n\n");

    // Format the prompt
    const prompt = `
      استخدم المعلومات التالية للإجابة على السؤال المعطى. إذا لم تجد الإجابة في السياق، فقط قل "لا أعرف". لا تخترع إجابات.
      
      السياق:
      ${retrievedContext}
      
      السؤال:
      ${message}
      
      الإجابة:
    `;

    // Query the LLM model
    const model = new ChatGoogleGenerativeAI({
      model: "gemini-1.5-flash",
      google_api_key: GOOGLE_API_KEY,
    });

    const response = await model.invoke(prompt);

    // Send back the response
    res.status(200).json({ response: response.content });
  } catch (error) {
    console.error("Error:", error);
    // res
    //   .status(500)
    //   .json({ message: "Internal server error", error: error.message });
  }
}
