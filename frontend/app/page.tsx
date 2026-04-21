import Link from "next/link";

const modules = [
  {
    href: "/collector",
    title: "Collector",
    description: "Collect new properties from Zillow, Realtor, LMS, Crexy",
    status: "active",
  },
  {
    href: "/zones",
    title: "Zone Locator",
    description: "Demographic and market data per region",
    status: "coming-soon",
  },
  {
    href: "/analysis",
    title: "Property Analysis",
    description: "Cap rate, ROI, and neighbor comparisons",
    status: "coming-soon",
  },
  {
    href: "/portfolio",
    title: "Portfolio Management",
    description: "Rental income, maintenance, and financials",
    status: "coming-soon",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Real State Investment Portal
        </h1>
        <p className="text-gray-500 mb-8">
          Collect, analyze, and manage real estate investments
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((mod) => (
            <div
              key={mod.href}
              className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <h2 className="text-xl font-semibold text-gray-800">
                  {mod.title}
                </h2>
                {mod.status === "coming-soon" && (
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded">
                    Coming soon
                  </span>
                )}
              </div>
              <p className="text-gray-500 text-sm mb-4">{mod.description}</p>
              {mod.status === "active" ? (
                <Link
                  href={mod.href}
                  className="text-blue-600 text-sm font-medium hover:underline"
                >
                  Open →
                </Link>
              ) : (
                <span className="text-gray-400 text-sm">Not yet available</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
