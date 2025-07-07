const agents = [
  { name: "Strategy Agent", status: "online" },
  { name: "Content Agent", status: "online" },
  { name: "Community Agent", status: "online" },
  { name: "Analytics Agent", status: "online" },
];

export default function AgentsPage() {
  return (
    <div className="max-w-3xl mx-auto mt-12">
      <h2 className="text-2xl font-bold mb-6">Agents</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {agents.map((agent) => (
          <div key={agent.name} className="bg-white dark:bg-gray-900 rounded-xl shadow p-6 flex items-center gap-4">
            <span className={`inline-block w-3 h-3 rounded-full ${agent.status === "online" ? "bg-green-500" : "bg-gray-400"}`} />
            <span className="font-medium text-lg">{agent.name}</span>
            <span className="ml-auto text-xs text-green-600 dark:text-green-400 font-semibold uppercase">{agent.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}