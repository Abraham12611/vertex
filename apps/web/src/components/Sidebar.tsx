"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  BarChart2,
  Settings as SettingsIcon,
  Menu,
} from "lucide-react";
import { useState } from "react";
import { Dialog } from "@headlessui/react";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Prompts", href: "/prompts", icon: MessageSquare },
  { name: "Agents", href: "/agents", icon: Users },
  { name: "Analytics", href: "/analytics", icon: BarChart2 },
  { name: "Settings", href: "/settings", icon: SettingsIcon },
];

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Mobile sidebar (slide-over)
  return (
    <>
      {/* Hamburger for mobile */}
      <button
        className="md:hidden p-2 fixed top-4 left-4 z-40 bg-white dark:bg-black rounded-full shadow"
        onClick={() => setOpen(true)}
        aria-label="Open sidebar"
      >
        <Menu className="w-6 h-6" />
      </button>
      {/* Slide-over sidebar for mobile */}
      <Dialog open={open} onClose={setOpen} className="relative z-50 md:hidden">
        <div className="fixed inset-0 bg-black/40" aria-hidden="true" />
        <div className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-900 p-6 flex flex-col gap-4 shadow-xl">
          <button
            className="self-end mb-4 text-gray-500 hover:text-black dark:hover:text-white"
            onClick={() => setOpen(false)}
            aria-label="Close sidebar"
          >
            ×
          </button>
          <nav className="flex flex-col gap-2">
            {navItems.map(({ name, href, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-4 py-2 rounded-lg font-medium transition-colors text-base ${
                  pathname === href
                    ? "bg-black text-white dark:bg-white dark:text-black"
                    : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                onClick={() => setOpen(false)}
              >
                <Icon className="w-5 h-5" />
                {name}
              </Link>
            ))}
          </nav>
        </div>
      </Dialog>
      {/* Fixed sidebar for desktop */}
      <aside className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 md:left-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 p-6 gap-4 z-30">
        <nav className="flex flex-col gap-2">
          {navItems.map(({ name, href, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg font-medium transition-colors text-base ${
                pathname === href
                  ? "bg-black text-white dark:bg-white dark:text-black"
                  : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
              }`}
            >
              <Icon className="w-5 h-5" />
              {name}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}