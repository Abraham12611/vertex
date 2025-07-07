import "../globals.css";
import { Sidebar } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { CommandBar } from "@/components/CommandBar";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  // TODO: Dynamically set page title based on route
  const pageTitle = "Vertex Workbench";
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black flex">
      <Sidebar />
      <div className="flex-1 flex flex-col md:ml-64 min-h-screen">
        <Topbar title={pageTitle} right={<ThemeToggle />} />
        <main className="flex-1 p-4 md:p-8 bg-transparent">
          {children}
        </main>
      </div>
      <CommandBar />
    </div>
  );
}