"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const steps = [
  {
    label: "Project Info",
    fields: [
      { name: "company", label: "Company Name", type: "text", required: true },
      { name: "website", label: "Website URL", type: "url", required: true },
      { name: "github", label: "GitHub URL", type: "url", required: false },
    ],
  },
  {
    label: "Product & Personas",
    fields: [
      { name: "product", label: "Product Overview", type: "textarea", required: true },
      { name: "personas", label: "Key Personas (comma-separated)", type: "text", required: true },
    ],
  },
  {
    label: "Goals & Style",
    fields: [
      { name: "goals", label: "Top Goals", type: "textarea", required: true },
      { name: "scope", label: "Scope", type: "textarea", required: false },
      { name: "style", label: "Style Guide Notes", type: "textarea", required: false },
    ],
  },
];

export default function BlueprintWizardPage() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<any>({});
  const [touched, setTouched] = useState<any>({});
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const current = steps[step];
  const isLast = step === steps.length - 1;

  function handleChange(e: any) {
    setForm({ ...form, [e.target.name]: e.target.value });
    setTouched({ ...touched, [e.target.name]: true });
  }

  function validate() {
    return current.fields.every(f => !f.required || form[f.name]?.trim());
  }

  function handleNext() {
    if (!validate()) return;
    setStep(s => s + 1);
  }

  function handlePrev() {
    setStep(s => s - 1);
  }

  function handleSubmit(e: any) {
    e.preventDefault();
    if (!validate()) return;
    setError(null);
    const id = Math.random().toString(36).slice(2, 10);
    localStorage.setItem(`blueprint_form_${id}`, JSON.stringify(form));
    router.push(`/blueprints/${id}`);
  }

  return (
    <div className="flex justify-center items-center min-h-[80vh] bg-[#09090b]">
      <form
        className="w-full max-w-2xl mx-auto p-10 rounded-3xl shadow-2xl border border-[#27272a] bg-[#18181b] flex flex-col gap-8"
        onSubmit={handleSubmit}
        autoComplete="off"
      >
        {/* Progress Bar */}
        <div className="flex items-center gap-4 mb-2">
          {steps.map((s, i) => (
            <div key={s.label} className="flex-1 flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white transition-all ${i <= step ? 'bg-[#007AFF] shadow-lg' : 'bg-[#27272a] text-gray-400'}`}>{i + 1}</div>
              <span className="text-xs mt-1 text-gray-400">{s.label}</span>
            </div>
          ))}
        </div>
        {/* Step Fields */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {current.fields.map(f => (
            <div key={f.name} className="flex flex-col gap-1">
              <label className="font-medium text-gray-200 mb-1">{f.label}{f.required && <span className="text-red-400">*</span>}</label>
              {f.type === "textarea" ? (
                <textarea
                  name={f.name}
                  value={form[f.name] || ""}
                  onChange={handleChange}
                  className="rounded-lg border border-[#27272a] px-3 py-2 text-base font-sans bg-[#18181b] text-white focus:ring-2 focus:ring-[#007AFF] shadow-inner placeholder-gray-500"
                  rows={3}
                />
              ) : (
                <input
                  type={f.type}
                  name={f.name}
                  value={form[f.name] || ""}
                  onChange={handleChange}
                  className="rounded-lg border border-[#27272a] px-3 py-2 text-base font-sans bg-[#18181b] text-white focus:ring-2 focus:ring-[#007AFF] shadow-inner placeholder-gray-500"
                />
              )}
              {touched[f.name] && f.required && !form[f.name]?.trim() && (
                <span className="text-xs text-red-400">Required</span>
              )}
            </div>
          ))}
        </div>
        {/* Navigation Buttons */}
        <div className="flex gap-4 justify-end mt-4">
          {step > 0 && (
            <button
              type="button"
              className="px-6 py-2 rounded-full bg-[#27272a] text-gray-200 font-semibold shadow hover:bg-[#232326]"
              onClick={handlePrev}
            >
              Previous
            </button>
          )}
          {!isLast && (
            <button
              type="button"
              className={`px-6 py-2 rounded-full bg-[#007AFF] text-white font-semibold shadow transition-all ${!validate() ? 'opacity-50 cursor-not-allowed' : 'hover:-translate-y-0.5 hover:shadow-lg'}`}
              onClick={handleNext}
              disabled={!validate()}
            >
              Next
            </button>
          )}
          {isLast && (
            <button
              type="submit"
              className={`px-8 py-2 rounded-full bg-[#007AFF] text-white font-semibold shadow transition-all ${!validate() ? 'opacity-50 cursor-not-allowed' : 'hover:-translate-y-0.5 hover:shadow-lg'}`}
              disabled={!validate()}
            >
              Generate Blueprint ↗︎
            </button>
          )}
        </div>
        {error && <div className="text-red-400 text-sm mt-2">{error}</div>}
      </form>
    </div>
  );
}