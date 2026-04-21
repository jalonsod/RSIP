"use client";

export default function CollectorPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Property Collector
        </h1>
        <p className="text-gray-500 mb-6">
          Collect new properties from configured sources based on your criteria.
        </p>
        {/* TODO: Criteria form and collection results table — implemented in feature/collector branch */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800 text-sm">
          Full UI under development in <code>feature/collector</code> branch.
        </div>
      </div>
    </main>
  );
}
