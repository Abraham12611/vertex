import { AnalyticsCharts } from "@/components/ui/AnalyticsCharts";
import { AnalyticsChartsGrid } from "@/components/ui/chart";

export default function AnalyticsPage() {
  return (
    <div className="max-w-5xl mx-auto mt-12 flex flex-col items-center gap-8">
      <div className="w-full">
        <h2 className="text-2xl font-bold mb-4 text-center">Analytics Dashboard</h2>
        {/* Single chart example */}
        <AnalyticsCharts />
        {/* Grid of charts example */}
        {/* <AnalyticsChartsGrid /> */}
      </div>
    </div>
  );
}