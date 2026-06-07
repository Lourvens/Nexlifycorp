import type { Citation } from "@/types/agent";

/** NDJSON events emitted by /api/chat after transforming LangGraph SSE. */
export type ChatStreamEvent =
  | { type: "text"; delta: string }
  | { type: "reasoning"; content: string }
  | { type: "citations"; items: Citation[] }
  | { type: "error"; message: string }
  | { type: "done" };

type LangGraphCitation = {
  document_title?: string;
  excerpt?: string;
  chunk_content?: string;
  source_category?: string;
  access_level?: string;
};

function isGenerateNodeMessage(tuple: unknown): boolean {
  if (!Array.isArray(tuple) || tuple.length < 2) return true;
  const meta = tuple[1];
  if (!meta || typeof meta !== "object") return true;
  const node = (meta as Record<string, unknown>).langgraph_node;
  return !node || node === "generate";
}

function extractTextDelta(data: unknown): string {
  if (data == null) return "";

  const tuples = Array.isArray(data) ? data : [data];
  let delta = "";

  for (const tuple of tuples) {
    if (!isGenerateNodeMessage(tuple)) continue;

    const msg = Array.isArray(tuple) ? tuple[0] : tuple;
    if (!msg || typeof msg !== "object") continue;

    const msgType = (msg as Record<string, unknown>).type;
    if (msgType && msgType !== "ai" && msgType !== "AIMessageChunk") continue;

    const content = (msg as Record<string, unknown>).content;
    if (typeof content === "string") {
      delta += content;
      continue;
    }

    if (Array.isArray(content)) {
      for (const block of content) {
        if (typeof block === "string") {
          delta += block;
        } else if (block && typeof block === "object") {
          const b = block as Record<string, unknown>;
          if (typeof b.text === "string") delta += b.text;
        }
      }
    }
  }

  return delta;
}

function mapCitations(raw: unknown): Citation[] {
  if (!Array.isArray(raw)) return [];

  return raw
    .filter((item): item is LangGraphCitation => !!item && typeof item === "object")
    .map((item) => ({
      source: item.document_title ?? "Unknown source",
      text: item.excerpt ?? item.chunk_content ?? "",
      doc_type: item.source_category ?? "unknown",
      access_level: item.access_level ?? "unknown",
    }));
}

function textFromMessage(msg: unknown): string {
  if (!msg || typeof msg !== "object") return "";
  const content = (msg as Record<string, unknown>).content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((block) =>
        typeof block === "string"
          ? block
          : block && typeof block === "object" && typeof (block as Record<string, unknown>).text === "string"
            ? (block as Record<string, unknown>).text
            : ""
      )
      .join("");
  }
  return "";
}

function extractNodeUpdate(data: unknown): {
  reasoning?: string;
  citations?: Citation[];
  answer?: string;
} {
  if (!data || typeof data !== "object") return {};

  const record = data as Record<string, unknown>;
  const reason = record.reason as Record<string, unknown> | undefined;
  const generate = record.generate as Record<string, unknown> | undefined;

  const result: {
    reasoning?: string;
    citations?: Citation[];
    answer?: string;
  } = {};

  if (reason) {
    if (typeof reason.reasoning_trace === "string") {
      result.reasoning = reason.reasoning_trace;
    }
    if (reason.citations) {
      result.citations = mapCitations(reason.citations);
    }
  }

  if (generate?.messages && Array.isArray(generate.messages)) {
    const aiMessages = generate.messages.filter(
      (m) =>
        m &&
        typeof m === "object" &&
        ((m as Record<string, unknown>).type === "ai" ||
          (m as Record<string, unknown>).role === "assistant")
    );
    const last = aiMessages.at(-1);
    const answer = textFromMessage(last);
    if (answer) result.answer = answer;
  }

  return result;
}

/** Parse LangGraph SSE bytes into ChatStreamEvent objects. */
export function parseLangGraphSse(
  chunk: string,
  buffer: string
): { events: ChatStreamEvent[]; buffer: string } {
  const combined = buffer + chunk;
  const parts = combined.split("\n\n");
  const remainder = parts.pop() ?? "";
  const events: ChatStreamEvent[] = [];

  for (const part of parts) {
    if (!part.trim()) continue;

    let eventType = "";
    let dataLine = "";

    for (const line of part.split("\n")) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim().split("|")[0];
      } else if (line.startsWith("data:")) {
        dataLine += line.slice(5).trim();
      }
    }

    if (!eventType || !dataLine) continue;

    try {
      const data = JSON.parse(dataLine) as unknown;

      if (eventType === "messages") {
        const delta = extractTextDelta(data);
        if (delta) events.push({ type: "text", delta });
      } else if (eventType === "updates") {
        const update = extractNodeUpdate(data);
        if (update.reasoning) {
          events.push({ type: "reasoning", content: update.reasoning });
        }
        if (update.citations?.length) {
          events.push({ type: "citations", items: update.citations });
        }
        if (update.answer) {
          events.push({ type: "text", delta: update.answer });
        }
      } else if (eventType === "error") {
        const err = data as { message?: string; error?: string };
        events.push({
          type: "error",
          message: err.message ?? err.error ?? "Agent error",
        });
      }
    } catch {
      // Skip malformed SSE frames
    }
  }

  return { events, buffer: remainder };
}

/** Consume NDJSON lines from the transformed API response. */
export function parseChatStreamLine(line: string): ChatStreamEvent | null {
  const trimmed = line.trim();
  if (!trimmed) return null;
  try {
    return JSON.parse(trimmed) as ChatStreamEvent;
  } catch {
    return null;
  }
}
