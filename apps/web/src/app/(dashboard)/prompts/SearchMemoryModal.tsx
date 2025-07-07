"use client";
import { useState } from "react";

export function SearchMemoryModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock search handler
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setResults([
        { content: "Sample snippet 1 about DevRel strategy.", score: 0.12 },
        { content: "Sample snippet 2 about community engagement.", score: 0.18 },
      ]);
      setLoading(false);
    }, 800);
  };

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 w-full max-w-lg relative">
        <button
          className="absolute top-2 right-2 text-gray-400 hover:text-black dark:hover:text-white"
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span role="img" aria-label="search">🔍</span> Search Memory
        </h3>
        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <input
            className="flex-1 px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm"
            placeholder="Enter your query..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            autoFocus
          />
          <button
            type="submit"
            className="px-4 py-2 rounded bg-black text-white dark:bg-white dark:text-black font-semibold text-sm hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors"
            disabled={loading || !query.trim()}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
        <div className="space-y-3">
          {results.length === 0 && !loading && (
            <div className="text-gray-400 text-sm text-center">No results yet.</div>
          )}
          {results.map((r, i) => (
            <div key={i} className="p-3 rounded bg-gray-100 dark:bg-gray-800 text-sm">
              <div className="mb-1">{r.content}</div>
              <div className="text-xs text-gray-500">Score: {r.score.toFixed(2)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}