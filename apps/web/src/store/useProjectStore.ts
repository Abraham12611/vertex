import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ProjectState {
  activeProjectId: string | null;
  setActiveProjectId: (id: string) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      activeProjectId: null,
      setActiveProjectId: (id) => set({ activeProjectId: id }),
      sidebarOpen: false,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
    }),
    {
      name: "vertex-project-store",
    }
  )
);