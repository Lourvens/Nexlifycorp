export type MessageRole = "user" | "assistant" | "system";

export interface Citation {
  text: string;
  source: string;
  doc_type: string;
  access_level: string;
  url?: string;
}

export interface RetrievedChunk {
  content: string;
  metadata: {
    source: string;
    doc_type: string;
    access_level: string;
    content_type: string;
    chunk_index: number;
  };
  score?: number;
}

export interface AgentState {
  messages: Array<{
    role: MessageRole;
    content: string;
  }>;
  route_key?: "public_only" | "internal_only" | "both";
  retrieved_chunks?: RetrievedChunk[];
  reasoning_trace?: string;
  citations?: Citation[];
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt?: Date;
  reasoning?: string;
  citations?: Citation[];
}

export interface UIMessage {
  id: string;
  role: MessageRole;
  content: string | Array<{
    type: "text";
    text: string;
  } | {
    type: "tool-call";
    toolCallId: string;
    toolName: string;
    args: Record<string, unknown>;
  }>;
}