import { NextRequest, NextResponse } from "next/server";
import { createLangGraphNdjsonStream } from "@/lib/langgraph-stream-transform";

const LANGGRAPH_API_URL = process.env.LANGGRAPH_API_URL || "http://localhost:2024";
const ASSISTANT_ID = "risk_qa_agent";

export const maxDuration = 300;

type IncomingMessage = { role: string; content: string };

function toLangGraphMessages(messages: IncomingMessage[]) {
  return messages.map((m) => ({
    role: m.role === "user" ? "human" : m.role === "assistant" ? "ai" : m.role,
    content: m.content,
  }));
}

export async function POST(req: NextRequest) {
  try {
    const { messages, threadId } = await req.json();

    // Create or get thread
    let thread_id = threadId;
    if (!thread_id) {
      // Create new thread via LangGraph API
      const threadRes = await fetch(`${LANGGRAPH_API_URL}/threads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!threadRes.ok) throw new Error("Failed to create thread");
      const thread = await threadRes.json();
      thread_id = thread.thread_id;
    }

    // LangGraph Server API: POST /threads/{thread_id}/runs/stream
    // Body requires assistant_id + input (not top-level messages).
    // See https://docs.langchain.com/oss/python/langgraph/local-server
    const response = await fetch(
      `${LANGGRAPH_API_URL}/threads/${thread_id}/runs/stream`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assistant_id: ASSISTANT_ID,
          input: { messages: toLangGraphMessages(messages) },
          stream_mode: ["messages-tuple", "updates"],
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`LangGraph API error ${response.status}: ${error}`);
    }

    if (!response.body) {
      throw new Error("LangGraph API returned empty stream");
    }

    // Transform LangGraph SSE → NDJSON the chat UI can render
    const transformed = createLangGraphNdjsonStream(response.body);

    return new Response(transformed, {
      headers: {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Thread-ID": thread_id,
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}