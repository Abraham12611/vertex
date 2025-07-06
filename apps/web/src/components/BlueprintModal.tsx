import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export function BlueprintModal({ open, onClose, onOpenDetail, blueprint }: {
  open: boolean;
  onClose: () => void;
  onOpenDetail: () => void;
  blueprint: any;
}) {
  // Extract section keys from blueprint
  const sectionKeys = blueprint ? Object.keys(blueprint) : [];
  const [streamed, setStreamed] = useState<number>(0);

  useEffect(() => {
    if (!open || !blueprint) return;
    setStreamed(0);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setStreamed(i);
      if (i >= sectionKeys.length) clearInterval(interval);
    }, 400);
    return () => clearInterval(interval);
  }, [open, blueprint]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="relative w-full max-w-4xl bg-gradient-to-br from-[#F5F7FA] to-[#E9ECF0] rounded-3xl shadow-2xl p-10 flex flex-col gap-8"
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 40, opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 24 }}
          >
            {/* Progress Dots */}
            <div className="flex gap-2 justify-center mb-2">
              {sectionKeys.map((_, i) => (
                <span
                  key={i}
                  className={`w-3 h-3 rounded-full transition-all ${i < streamed ? 'bg-[#007AFF]' : 'bg-gray-300'}`}
                />
              ))}
            </div>
            <div className="text-2xl font-bold text-center mb-2" style={{ fontFamily: 'SF Pro Rounded, sans-serif' }}>
              Blueprint Report
            </div>
            {/* Section Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {blueprint && sectionKeys.slice(0, streamed).map((key, idx) => (
                <motion.div
                  key={key}
                  className="rounded-2xl bg-white/80 shadow-xl border border-white/40 p-6 flex flex-col gap-2"
                  initial={{ y: 30, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.06 }}
                >
                  <div className="text-lg font-semibold mb-1" style={{ fontFamily: 'SF Pro Display, sans-serif' }}>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                  <pre className="text-gray-700 text-sm whitespace-pre-wrap" style={{ fontFamily: 'SF Pro Text, sans-serif' }}>{JSON.stringify(blueprint[key], null, 2)}</pre>
                </motion.div>
              ))}
            </div>
            {/* CTA Button */}
            <button
              className="fixed bottom-10 right-10 px-8 py-3 rounded-full bg-[#34C759] text-white text-lg font-semibold shadow-lg transition-transform hover:-translate-y-1 hover:shadow-2xl"
              style={{ boxShadow: 'inset 0 2px 8px #fff6, 0 4px 24px #34C75933' }}
              onClick={onOpenDetail}
              disabled={streamed < sectionKeys.length}
            >
              Open Detailed Planner ⤵︎
            </button>
            {/* Close Button */}
            <button
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-700 text-2xl font-bold"
              onClick={onClose}
              aria-label="Close"
            >
              ×
            </button>
            {!blueprint && (
              <div className="text-center text-gray-500 text-lg">Loading...</div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}