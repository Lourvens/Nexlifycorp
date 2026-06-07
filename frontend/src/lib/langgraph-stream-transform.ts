import {
  parseLangGraphSse,
  type ChatStreamEvent,
} from "@/lib/langgraph-stream";

/** Transform raw LangGraph SSE into NDJSON ChatStreamEvents for the client. */
export function createLangGraphNdjsonStream(
  source: ReadableStream<Uint8Array>
): ReadableStream<Uint8Array> {
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();
  let buffer = "";

  return source.pipeThrough(
    new TransformStream<Uint8Array, Uint8Array>({
      transform(chunk, controller) {
        const text = decoder.decode(chunk, { stream: true });
        const { events, buffer: nextBuffer } = parseLangGraphSse(text, buffer);
        buffer = nextBuffer;

        for (const event of events) {
          controller.enqueue(encoder.encode(`${JSON.stringify(event)}\n`));
        }
      },
      flush(controller) {
        if (buffer.trim()) {
          const { events } = parseLangGraphSse("\n\n", buffer);
          for (const event of events) {
            controller.enqueue(encoder.encode(`${JSON.stringify(event)}\n`));
          }
        }
        const done: ChatStreamEvent = { type: "done" };
        controller.enqueue(encoder.encode(`${JSON.stringify(done)}\n`));
      },
    })
  );
}
