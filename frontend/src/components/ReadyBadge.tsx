import type { PatientReadiness } from "../api/types";

export function ReadyBadge({ readiness }: { readiness: PatientReadiness | null }) {
  if (readiness === null) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500">
        …
      </span>
    );
  }
  if (readiness.is_ready) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
        Ready ✓
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
      Not ready
    </span>
  );
}
