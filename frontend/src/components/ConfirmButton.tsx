import { useState } from "react";
import {
  ApiError,
  confirmAppointment,
} from "../api/client";
import type { ConfirmFailure, UnconfirmableBlocker } from "../api/types";

interface Props {
  appointmentId: number;
  status: string;
  onConfirmed: () => void;
}

export function ConfirmButton({ appointmentId, status, onConfirmed }: Props) {
  const [busy, setBusy] = useState(false);
  const [blockers, setBlockers] = useState<UnconfirmableBlocker[] | null>(null);
  const [unexpectedError, setUnexpectedError] = useState<string | null>(null);

  if (status === "CONFIRMED") {
    return (
      <div className="rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 px-3 py-2 text-sm font-medium">
        Confirmed
      </div>
    );
  }

  async function onClick() {
    setBusy(true);
    setBlockers(null);
    setUnexpectedError(null);
    try {
      await confirmAppointment(appointmentId);
      onConfirmed();
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        const parsed = err.parsed<ConfirmFailure>();
        setBlockers(parsed?.detail.blockers ?? []);
      } else {
        setUnexpectedError(err instanceof Error ? err.message : "Unknown error");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={onClick}
        disabled={busy}
        className="inline-flex items-center px-4 py-2 rounded-md bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 disabled:opacity-50"
      >
        {busy ? "Confirming…" : "Confirm Session"}
      </button>
      {blockers !== null && blockers.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-rose-800">
            Cannot confirm — {blockers.length} blocker
            {blockers.length === 1 ? "" : "s"}:
          </div>
          <ul className="space-y-2">
            {blockers.map((b) => (
              <li
                key={b.reason}
                className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2"
              >
                <div className="text-sm font-medium text-rose-800">{b.reason}</div>
                <div className="text-sm text-rose-700">{b.message}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
      {unexpectedError !== null && (
        <div className="text-sm text-rose-700">{unexpectedError}</div>
      )}
    </div>
  );
}
