"use client";

export function CommandBar() {
  return (
    <button
      className="fixed bottom-6 right-6 z-40 px-4 py-2 rounded-full bg-black text-white dark:bg-white dark:text-black shadow-lg text-sm font-medium opacity-80 hover:opacity-100 transition-all"
      style={{ pointerEvents: "auto" }}
      disabled
    >
      CommandBar (Coming Soon)
    </button>
  );
}