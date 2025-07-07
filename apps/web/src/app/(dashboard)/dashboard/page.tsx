export default function DashboardPage() {
  return (
    <div className="max-w-xl mx-auto mt-12 flex flex-col gap-8">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-8 text-center">
        <h2 className="text-2xl font-bold mb-2">Welcome to Vertex</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Your DevRel automation workbench.
        </p>
        <div className="inline-block px-4 py-2 rounded bg-gray-100 dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-200">
          [Project Switcher Coming Soon]
        </div>
      </div>
    </div>
  );
}