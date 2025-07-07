"use client";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  // Placeholder: add theme switching logic with next-themes later
  return (
    <button
      className="rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      aria-label="Toggle theme"
      type="button"
    >
      <Sun className="w-5 h-5 block dark:hidden" />
      <Moon className="w-5 h-5 hidden dark:block" />
    </button>
  );
}