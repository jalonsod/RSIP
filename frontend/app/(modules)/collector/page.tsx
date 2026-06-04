"use client";

import { useState, useEffect } from "react";

type PropertyType =
  | "single_family"
  | "multi_family"
  | "condo"
  | "townhouse"
  | "commercial";

interface CollectionCriteria {
  min_price: number;
  max_price: number;
  property_types: PropertyType[];
  zip_codes: string[];
  min_sqft?: number | null;
  max_sqft?: number | null;
  min_year_built?: number | null;
}

interface CollectionRunResult {
  source: string;
  properties_found: number;
  properties_new: number;
  properties_skipped: number;
  errors: string[];
}

const PROPERTY_TYPES: { value: PropertyType; label: string }[] = [
  { value: "single_family", label: "Single Family" },
  { value: "multi_family", label: "Multi Family" },
  { value: "condo", label: "Condo" },
  { value: "townhouse", label: "Townhouse" },
  { value: "commercial", label: "Commercial" },
];

const DEFAULT_CRITERIA: CollectionCriteria = {
  min_price: 100000,
  max_price: 1000000,
  property_types: [],
  zip_codes: [],
  min_sqft: null,
  max_sqft: null,
  min_year_built: null,
};

function CollectorCriteriaForm() {
  const [criteria, setCriteria] = useState<CollectionCriteria>(DEFAULT_CRITERIA);
  const [zipInput, setZipInput] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");

  useEffect(() => {
    fetch("/api/v1/collector/criteria")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => { if (data) setCriteria(data); })
      .catch(() => {});
  }, []);

  const togglePropertyType = (type: PropertyType) =>
    setCriteria((prev) => ({
      ...prev,
      property_types: prev.property_types.includes(type)
        ? prev.property_types.filter((t) => t !== type)
        : [...prev.property_types, type],
    }));

  const handleAddZip = () => {
    const zips = zipInput
      .split(",")
      .map((z) => z.trim())
      .filter((z) => z && !criteria.zip_codes.includes(z));
    if (zips.length > 0) {
      setCriteria((prev) => ({ ...prev, zip_codes: [...prev.zip_codes, ...zips] }));
      setZipInput("");
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus("idle");
    try {
      const res = await fetch("/api/v1/collector/criteria", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...criteria,
          min_sqft: criteria.min_sqft || null,
          max_sqft: criteria.max_sqft || null,
          min_year_built: criteria.min_year_built || null,
        }),
      });
      if (!res.ok) throw new Error();
      setSaveStatus("success");
    } catch {
      setSaveStatus("error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-5">Collection Criteria</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Price ($)</label>
          <input
            type="number"
            value={criteria.min_price}
            onChange={(e) =>
              setCriteria((p) => ({ ...p, min_price: Number(e.target.value) }))
            }
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Price ($)</label>
          <input
            type="number"
            value={criteria.max_price}
            onChange={(e) =>
              setCriteria((p) => ({ ...p, max_price: Number(e.target.value) }))
            }
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Sqft <span className="text-gray-400">(optional)</span>
          </label>
          <input
            type="number"
            value={criteria.min_sqft ?? ""}
            onChange={(e) =>
              setCriteria((p) => ({
                ...p,
                min_sqft: e.target.value ? Number(e.target.value) : null,
              }))
            }
            placeholder="Any"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Sqft <span className="text-gray-400">(optional)</span>
          </label>
          <input
            type="number"
            value={criteria.max_sqft ?? ""}
            onChange={(e) =>
              setCriteria((p) => ({
                ...p,
                max_sqft: e.target.value ? Number(e.target.value) : null,
              }))
            }
            placeholder="Any"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Year Built <span className="text-gray-400">(optional)</span>
          </label>
          <input
            type="number"
            value={criteria.min_year_built ?? ""}
            onChange={(e) =>
              setCriteria((p) => ({
                ...p,
                min_year_built: e.target.value ? Number(e.target.value) : null,
              }))
            }
            placeholder="Any"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="mt-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">Property Types</label>
        <div className="flex flex-wrap gap-4">
          {PROPERTY_TYPES.map(({ value, label }) => (
            <label
              key={value}
              className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                checked={criteria.property_types.includes(value)}
                onChange={() => togglePropertyType(value)}
                className="w-4 h-4 accent-blue-600"
              />
              {label}
            </label>
          ))}
        </div>
      </div>

      <div className="mt-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">Zip Codes</label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={zipInput}
            onChange={(e) => setZipInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddZip()}
            placeholder="Enter zip codes, comma-separated"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleAddZip}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors"
          >
            Add
          </button>
        </div>
        {criteria.zip_codes.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {criteria.zip_codes.map((zip) => (
              <span
                key={zip}
                className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded text-sm"
              >
                {zip}
                <button
                  onClick={() =>
                    setCriteria((p) => ({
                      ...p,
                      zip_codes: p.zip_codes.filter((z) => z !== zip),
                    }))
                  }
                  className="text-blue-400 hover:text-blue-700 ml-0.5 font-bold leading-none"
                  aria-label={`Remove ${zip}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? "Saving…" : "Save Criteria"}
        </button>
        {saveStatus === "success" && (
          <span className="text-green-600 text-sm">Criteria saved</span>
        )}
        {saveStatus === "error" && (
          <span className="text-red-600 text-sm">Failed to save — check backend connection</span>
        )}
      </div>
    </div>
  );
}

function CollectionResultsTable({ results }: { results: CollectionRunResult[] }) {
  if (results.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
        No properties found.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Source</th>
            <th className="text-right px-4 py-3 font-medium text-gray-600">Found</th>
            <th className="text-right px-4 py-3 font-medium text-gray-600">New</th>
            <th className="text-right px-4 py-3 font-medium text-gray-600">Skipped</th>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Errors</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {results.map((r) => (
            <tr key={r.source} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-800 capitalize">{r.source}</td>
              <td className="px-4 py-3 text-right text-gray-700">{r.properties_found}</td>
              <td className="px-4 py-3 text-right text-green-600 font-medium">
                {r.properties_new}
              </td>
              <td className="px-4 py-3 text-right text-gray-500">{r.properties_skipped}</td>
              <td className="px-4 py-3">
                {r.errors.length === 0 ? (
                  <span className="text-gray-300">—</span>
                ) : (
                  <ul className="list-disc list-inside text-red-500 space-y-0.5">
                    {r.errors.map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function CollectorPage() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<CollectionRunResult[] | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setRunError(null);
    setResults(null);
    try {
      const res = await fetch("/api/v1/collector/run", { method: "POST" });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error((data as { detail?: string }).detail ?? "Run failed");
      }
      setResults(await res.json());
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setRunning(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">Property Collector</h1>
            <p className="text-gray-500 text-sm">
              Collect new properties from configured sources based on your criteria.
            </p>
          </div>
          <button
            onClick={handleRun}
            disabled={running}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {running && (
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}
            {running ? "Running…" : "Run Collection"}
          </button>
        </div>

        <div className="space-y-6">
          <CollectorCriteriaForm />

          {runError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
              {runError}
            </div>
          )}

          {results !== null && (
            <div>
              <h2 className="text-base font-semibold text-gray-800 mb-3">Collection Results</h2>
              <CollectionResultsTable results={results} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
