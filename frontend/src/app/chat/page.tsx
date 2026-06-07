"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ChatMessage, Citation } from "@/types/agent";
import { parseChatStreamLine } from "@/lib/langgraph-stream";
import { Send, Loader2, Brain, FileText, ChevronDown, ChevronUp } from "lucide-react";

function formatCitation(citation: Citation, index: number) {
  return (
    <div key={index} className="flex items-start gap-2 p-2 rounded-md bg-muted/50 text-xs">
      <span className="font-medium text-primary shrink-0">[{index + 1}]</span>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{citation.source}</p>
        <p className="text-muted-foreground truncate">{citation.text}</p>
        <div className="flex gap-1 mt-1">
          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
            {citation.doc_type}
          </span>
          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
            {citation.access_level}
          </span>
        </div>
      </div>
    </div>
  );
}

function ReasoningPanel({ reasoning }: { reasoning: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border rounded-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full p-3 text-left text-sm font-medium hover:bg-muted/50 transition-colors"
      >
        <Brain className="w-4 h-4" />
        <span>Analysis & Reasoning</span>
        {isOpen ? <ChevronUp className="w-4 h-4 ml-auto" /> : <ChevronDown className="w-4 h-4 ml-auto" />}
      </button>
      {isOpen && (
        <div className="p-3 pt-0 text-sm text-muted-foreground whitespace-pre-wrap border-t">
          {reasoning}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        }`}
      >
        <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">
          {message.content || (isUser ? "" : "…")}
        </div>

        {message.reasoning && !isUser && (
          <div className="mt-3">
            <ReasoningPanel reasoning={message.reasoning} />
          </div>
        )}

        {message.citations && message.citations.length > 0 && !isUser && (
          <div className="mt-3 space-y-1">
            <div className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
              <FileText className="w-3 h-3" />
              <span>Sources ({message.citations.length})</span>
            </div>
            <div className="space-y-1">
              {message.citations.slice(0, 3).map((c, i) => formatCitation(c, i))}
              {message.citations.length > 3 && (
                <p className="text-xs text-muted-foreground pl-2">
                  +{message.citations.length - 3} more sources
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      createdAt: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
          threadId,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error ?? "Failed to get response");
      }

      const newThreadId = response.headers.get("X-Thread-ID");
      if (newThreadId) setThreadId(newThreadId);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      const assistantId = (Date.now() + 1).toString();
      let assistantMessage: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      const updateAssistant = (patch: Partial<ChatMessage>) => {
        assistantMessage = { ...assistantMessage, ...patch };
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? assistantMessage : m))
        );
      };

      if (reader) {
        let lineBuffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          lineBuffer += decoder.decode(value, { stream: true });
          const lines = lineBuffer.split("\n");
          lineBuffer = lines.pop() ?? "";

          for (const line of lines) {
            const event = parseChatStreamLine(line);
            if (!event) continue;

            if (event.type === "text") {
              const nextContent = event.delta.startsWith(assistantMessage.content)
                ? event.delta
                : assistantMessage.content + event.delta;
              updateAssistant({ content: nextContent });
            } else if (event.type === "reasoning") {
              updateAssistant({ reasoning: event.content });
            } else if (event.type === "citations") {
              updateAssistant({ citations: event.items });
            } else if (event.type === "error") {
              throw new Error(event.message);
            }
          }
        }
      }

      if (!assistantMessage.content.trim()) {
        updateAssistant({
          content: "The agent finished without a response. Please try again.",
        });
      }
    } catch (error) {
      console.error("Chat error:", error);
      const message =
        error instanceof Error ? error.message : "Sorry, I encountered an error. Please try again.";
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === "assistant" && !last.content.trim()) {
          return prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, content: message } : m
          );
        }
        return [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: message,
            createdAt: new Date(),
          },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b px-6 py-4">
        <h1 className="text-xl font-semibold">NexlifyCorp Risk Intelligence</h1>
        <p className="text-sm text-muted-foreground">
          Ask questions about SEC filings and internal documents
        </p>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Brain className="w-12 h-12 text-muted-foreground/50 mb-4" />
            <h2 className="text-lg font-medium">Start a conversation</h2>
            <p className="text-sm text-muted-foreground max-w-md">
              Ask about risk factors, financial statements, management discussion,
              or any topic covered in SEC filings and internal NexlifyCorp documents.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && messages.at(-1)?.role === "user" && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg px-4 py-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm text-muted-foreground">Analyzing...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <footer className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about risk factors, financial data, or internal documents..."
            className="min-h-[56px] max-h-[200px] resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button type="submit" size="icon" disabled={!input.trim() || isLoading}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
        <p className="text-xs text-muted-foreground text-center mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </footer>
    </div>
  );
}