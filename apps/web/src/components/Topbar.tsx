"use client";
import { ReactNode } from "react";

export function Topbar({ title, right }: { title: string; right?: ReactNode }) {
  return (
    <header className="sticky top-0 z-20 w-full h-16 flex items-center justify-between px-4 md:px-8 bg-white/80 dark:bg-black/80 backdrop-blur border-b border-gray-200 dark:border-gray-800 shadow-sm">
      <h1 className="text-xl sm:text-2xl font-semibold tracking-tight truncate">
        {title}
      </h1>
      <div className="flex items-center gap-2">{right}</div>
    </header>
  );
}