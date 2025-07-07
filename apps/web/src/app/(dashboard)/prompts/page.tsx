"use client";
import { useState } from "react";
import { SearchMemoryModal } from "./SearchMemoryModal";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

async function fetchPrompts() {
  const { data } = await api.get("/mock/prompts");
  return data;
}

export default function PromptsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["prompts"],
    queryFn: fetchPrompts,
  });
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <h2 className="text-2xl font-bold mb-6">Prompt History</h2>
      <button
        className="mb-4 px-4 py-2 rounded bg-black text-white dark:bg-white dark:text-black font-semibold text-sm hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors"
        onClick={() => setModalOpen(true)}
      >
        🔍 Search Memory
      </button>
      <SearchMemoryModal open={modalOpen} onClose={() => setModalOpen(false)} />
      {isLoading ? (
        <div className="text-gray-400">Loading...</div>
      ) : error ? (
        <div className="text-red-500">Failed to load prompts.</div>
      ) : (
        <table className="w-full bg-white dark:bg-gray-900 rounded-xl shadow overflow-hidden">
          <thead>
            <tr className="text-left text-gray-500 dark:text-gray-400 text-sm">
              <th className="px-4 py-2">Prompt</th>
              <th className="px-4 py-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((row: { id: number; prompt: string; date: string }) => (
              <tr key={row.id} className="border-t border-gray-100 dark:border-gray-800">
                <td className="px-4 py-2">{row.prompt}</td>
                <td className="px-4 py-2 text-xs text-gray-400">{row.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}