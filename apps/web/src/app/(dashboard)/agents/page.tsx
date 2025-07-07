"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";

const agents = [
  { name: "Strategy Agent", status: "online" },
  { name: "Content Agent", status: "online" },
  { name: "Community Agent", status: "online" },
  { name: "Analytics Agent", status: "online" },
];

async function runAgents(input: string) {
  const { data } = await api.post("/mock/agents/run", { input });
  return data;
}

export default function AgentsPage() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const { mutate, isLoading, error } = useMutation({
    mutationFn: (input: string) => runAgents(input),
    onSuccess: (data) => setResults(data.results),
  });

  return (
    <div className="max-w-3xl mx-auto mt-12">
      <h2 className="text-2xl font-bold mb-6">Agents</h2>
      <div className="mb-4 flex gap-2">
        <input
          className="flex-1 px-3 py-2 rounded border"
          placeholder="Enter input for agents (optional)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          className="px-4 py-2 rounded bg-black text-white font-semibold"
          onClick={() => mutate(input)}
          disabled={isLoading}
        >
          {isLoading ? "Running..." : "Run Agents"}
        </button>
      </div>
      {error && (
        <div className="text-red-500 mb-4">Failed to run agents. Please try again.</div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {results.length > 0
          ? results.map((res) => (
              <div key={res.agent} className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
                <div className="font-bold">{res.agent}</div>
                <div className="mt-2 text-sm whitespace-pre-line">{res.output}</div>
              </div>
            ))
          : agents.map((agent) => (
              <div key={agent.name} className="bg-white dark:bg-gray-900 rounded-xl shadow p-6 flex items-center gap-4">
                <span className={`inline-block w-3 h-3 rounded-full ${agent.status === "online" ? "bg-green-500" : "bg-gray-400"}`} />
                <span className="font-medium text-lg">{agent.name}</span>
                <span className="ml-auto text-xs text-green-600 dark:text-green-400 font-semibold uppercase">{agent.status}</span>
              </div>
            ))}
      </div>
    </div>
  );
}