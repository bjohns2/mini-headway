import type { UnconfirmableBlocker } from "../api/types";

export function BlockerList({ blockers }: { blockers: UnconfirmableBlocker[] }) {
  if (blockers.length === 0) return null;
  return (
    <ul className="space-y-2">
      {blockers.map((b) => (
        <li
          key={b.reason}
          className="flex gap-3 items-start rounded-md border border-rose-200 bg-rose-50 px-3 py-2"
        >
          <span className="mt-0.5 text-rose-600">⚠</span>
          <div>
            <div className="text-sm font-medium text-rose-800">{b.reason}</div>
            <div className="text-sm text-rose-700">{b.message}</div>
          </div>
        </li>
      ))}
    </ul>
  );
}
