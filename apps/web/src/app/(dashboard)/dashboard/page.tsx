"use client";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  return (
    <div className="flex justify-center items-center min-h-[70vh] bg-[#09090b]">
      <div className="relative w-full max-w-2xl mx-auto p-10 rounded-3xl shadow-2xl border border-[#27272a] bg-[#18181b] flex flex-col items-center gap-8">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#18181b] rounded-full px-6 py-2 shadow text-xs font-semibold tracking-widest border border-[#27272a] text-white">
          Vertex ▸ Blueprint
        </div>
        <h2 className="text-4xl font-bold mb-2 text-center text-white" style={{ fontFamily: 'SF Pro Rounded, sans-serif' }}>
          Welcome to Vertex
        </h2>
        <p className="text-lg text-gray-200 text-center max-w-xl">
          Instantly generate a DevRel strategy blueprint for your developer product. Start the onboarding wizard to get a custom plan powered by AI.
        </p>
        <button
          className="mt-4 px-8 py-3 rounded-full bg-[#007AFF] text-white text-lg font-semibold shadow-lg transition-transform hover:-translate-y-1 hover:shadow-2xl focus:outline-none focus:ring-2 focus:ring-[#007AFF]/40"
          style={{ boxShadow: 'inset 0 2px 8px #2226, 0 4px 24px #007aff33' }}
          onClick={() => router.push("/dashboard/blueprint-wizard")}
        >
          Generate Blueprint ↗︎
        </button>
      </div>
    </div>
  );
}