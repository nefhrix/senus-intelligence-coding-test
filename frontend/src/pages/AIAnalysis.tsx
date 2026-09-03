import {
  useEffect,
  useRef,
  useState,
} from "react";


import { useMutation } from "@tanstack/react-query";

import { generateBoardInsights } from "../api/ai";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const prompts = [
  "Give me a Board-level overview",
  "What are the biggest financial risks?",
  "Analyse profitability",
  "Analyse cash and liquidity",
];

export default function AIAnalysis() {
  const [input, setInput] =
    useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const bottomRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const insightsMutation =
    useMutation({
      mutationFn: (
        question: string,
      ) =>
        generateBoardInsights(
          question,
        ),

      onSuccess: (data) => {
        setMessages(
          (current) => [
            ...current,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: data.insights,
            },
          ],
        );
      },
    });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [
    messages,
    insightsMutation.isPending,
  ]);

  function sendQuestion(
    question: string,
  ) {
    const cleanQuestion =
      question.trim();

    if (
      !cleanQuestion ||
      insightsMutation.isPending
    ) {
      return;
    }

    setMessages(
      (current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "user",
          content: cleanQuestion,
        },
      ],
    );

    setInput("");

    insightsMutation.mutate(
      cleanQuestion,
    );
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] flex-col">
      <header className="flex items-center justify-between pb-5">
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-950">
          AI Analysis
        </h1>

        <div className="flex items-center gap-2 font-mono text-[11px] text-zinc-500">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          QWEN3:8B
        </div>
      </header>

      <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-zinc-200 bg-zinc-50 px-5 py-3">
          <span className="font-mono text-xs font-semibold uppercase tracking-wider text-zinc-600">
            Board Intelligence
          </span>

          <span className="font-mono text-[10px] uppercase tracking-wider text-zinc-400">
            Validated Financial Data
          </span>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <EmptyState
              onPrompt={
                sendQuestion
              }
            />
          ) : (
            <div className="mx-auto max-w-4xl space-y-8">
              {messages.map(
                (message) => (
                  <Message
                    key={message.id}
                    message={
                      message
                    }
                  />
                ),
              )}

              {insightsMutation.isPending && (
                <Thinking />
              )}

              {insightsMutation.isError && (
                <div className="ml-12 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {insightsMutation.error
                    instanceof Error
                    ? insightsMutation
                        .error.message
                    : "Analysis failed."}
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <div className="border-t border-zinc-200 bg-zinc-50 p-4">
         <form
  onSubmit={(event) => {
    event.preventDefault();
    sendQuestion(input);
  }}
  className="mx-auto flex max-w-4xl gap-3"
>
            <div className="flex flex-1 items-center rounded-lg border border-zinc-300 bg-white px-4 transition focus-within:border-zinc-500">
              <span className="mr-3 font-mono text-sm text-zinc-400">
                &gt;
              </span>

              <input
                value={input}
                onChange={(event) =>
                  setInput(
                    event.target.value,
                  )
                }
                placeholder="Ask about revenue, profitability, liquidity or risk..."
                className="h-12 flex-1 bg-transparent text-sm text-zinc-900 outline-none placeholder:text-zinc-400"
              />
            </div>

            <button
              type="submit"
              disabled={
                !input.trim() ||
                insightsMutation.isPending
              }
              className="h-12 rounded-lg bg-zinc-950 px-6 text-sm font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}

function EmptyState({
  onPrompt,
}: {
  onPrompt: (
    prompt: string,
  ) => void;
}) {
  return (
    <div className="flex min-h-[420px] items-center justify-center">
      <div className="w-full max-w-xl">
        <p className="font-mono text-xs font-medium uppercase tracking-wider text-zinc-400">
          Financial Intelligence
        </p>

        <h2 className="mt-3 text-2xl font-semibold tracking-tight text-zinc-950">
          Ask about the business
        </h2>

        <p className="mt-3 text-sm leading-6 text-zinc-500">
          Analyse revenue, margins,
          profitability, cash flow,
          liquidity, balance sheet
          strength and financial risk.
        </p>

        <div className="mt-7 grid gap-3 sm:grid-cols-2">
          {prompts.map(
            (prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() =>
                  onPrompt(prompt)
                }
                className="rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-4 text-left text-sm font-medium text-zinc-700 transition hover:border-zinc-400 hover:bg-white"
              >
                {prompt}
              </button>
            ),
          )}
        </div>
      </div>
    </div>
  );
}

function Message({
  message,
}: {
  message: Message;
}) {
  const isUser =
    message.role === "user";

  return (
    <div className="flex gap-4">
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md font-mono text-[9px] font-semibold ${
          isUser
            ? "border border-zinc-300 bg-white text-zinc-600"
            : "bg-zinc-950 text-white"
        }`}
      >
        {isUser
          ? "YOU"
          : "AI"}
      </div>

      <div className="min-w-0 flex-1">
        <p className="mb-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
          {isUser
            ? "Query"
            : "Analysis"}
        </p>

        {isUser ? (
          <p className="text-sm font-medium leading-6 text-zinc-900">
            {message.content}
          </p>
        ) : (
          <AssistantResponse
            text={
              message.content
            }
          />
        )}
      </div>
    </div>
  );
}

function AssistantResponse({
  text,
}: {
  text: string;
}) {
  const lines = text
    .split("\n")
    .map((line) =>
      line.trim(),
    )
    .filter(Boolean);

  return (
    <div className="space-y-3">
      {lines.map(
        (line, index) => {
          const cleanLine = line
            .replace(
              /^#{1,6}\s*/,
              "",
            )
            .replace(
              /\*\*/g,
              "",
            )
            .trim();

          const isBullet =
            /^[-•]\s+/.test(
              cleanLine,
            );

          const isHeading =
            !isBullet &&
            cleanLine.length < 45 &&
            !cleanLine.endsWith(
              ".",
            );

          if (isHeading) {
            return (
              <div
                key={index}
                className="pt-3 first:pt-0"
              >
                <span className="inline-flex rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 font-mono text-[10px] font-semibold uppercase tracking-wider text-zinc-600">
                  {cleanLine.replace(
                    /:$/,
                    "",
                  )}
                </span>
              </div>
            );
          }

          if (isBullet) {
            return (
              <div
                key={index}
                className="flex gap-3"
              >
                <span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-400" />

                <p className="text-sm leading-7 text-zinc-600">
                  {cleanLine.replace(
                    /^[-•]\s+/,
                    "",
                  )}
                </p>
              </div>
            );
          }

          return (
            <p
              key={index}
              className="text-sm leading-7 text-zinc-600"
            >
              {cleanLine}
            </p>
          );
        },
      )}
    </div>
  );
}

function Thinking() {
  return (
    <div className="flex gap-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-zinc-950 font-mono text-[9px] font-semibold text-white">
        AI
      </div>

      <div className="flex items-center gap-1 pt-3">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-zinc-400" />
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-zinc-400 [animation-delay:150ms]" />
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-zinc-400 [animation-delay:300ms]" />
      </div>
    </div>
  );
}