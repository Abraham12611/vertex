"use client";

import { useState } from "react";

const tabs = ["Profile", "Project", "Billing"];

export default function SettingsPage() {
  const [active, setActive] = useState(0);
  return (
    <div className="max-w-2xl mx-auto mt-12">
      <h2 className="text-2xl font-bold mb-6">Settings</h2>
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-800 mb-8">
        {tabs.map((tab, i) => (
          <button
            key={tab}
            className={`px-4 py-2 font-medium rounded-t transition-colors focus:outline-none ${
              i === active
                ? "bg-white dark:bg-gray-900 border-b-2 border-black dark:border-white"
                : "text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white"
            }`}
            onClick={() => setActive(i)}
          >
            {tab}
          </button>
        ))}
      </div>
      <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-xl shadow text-center text-gray-400">
        [Stub content for {tabs[active]}]
      </div>
    </div>
  );
}