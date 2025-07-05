import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen items-center justify-center px-4 py-12 sm:px-8 bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-900">
      <main className="flex flex-1 flex-col items-center justify-center w-full max-w-2xl text-center gap-8">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-4">
          Vertex
        </h1>
        <p className="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-xl mx-auto">
          DevRel Automation Platform for Developer-Focused Startups
        </p>
        <div className="w-full flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/workbench"
            className="inline-block rounded-full bg-black text-white dark:bg-white dark:text-black px-8 py-3 text-base sm:text-lg font-semibold shadow-md hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors"
          >
            Enter Workbench
          </Link>
        </div>
      </main>
      <footer className="mt-12 text-xs text-gray-400 dark:text-gray-600">
        &copy; {new Date().getFullYear()} Vertex. All rights reserved.
      </footer>
    </div>
  );
}
