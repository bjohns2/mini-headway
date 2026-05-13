import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getPatientReadiness, listAppointments } from "../api/client";
import type { AppointmentWithPatient, PatientReadiness } from "../api/types";
import { ReadyBadge } from "../components/ReadyBadge";
import { formatDate, formatTime } from "../lib/format";

function isoDate(d: Date): string {
  // YYYY-MM-DD in the local timezone (avoids the UTC drift you'd get from
  // d.toISOString().slice(0,10) when the user is west of UTC).
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${dd}`;
}

function shiftDay(iso: string, deltaDays: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const next = new Date(y, m - 1, d + deltaDays);
  return isoDate(next);
}

const TODAY_ISO = isoDate(new Date());

export default function DayView() {
  const [day, setDay] = useState<string>(TODAY_ISO);
  const [appointments, setAppointments] = useState<AppointmentWithPatient[] | null>(
    null,
  );
  const [readinessByPatient, setReadinessByPatient] = useState<
    Record<number, PatientReadiness>
  >({});

  useEffect(() => {
    let cancelled = false;
    setAppointments(null);
    listAppointments(day).then((appts) => {
      if (cancelled) return;
      setAppointments(appts);
      const uniquePatientIds = Array.from(new Set(appts.map((a) => a.patient_id)));
      Promise.all(uniquePatientIds.map((id) => getPatientReadiness(id))).then(
        (results) => {
          if (cancelled) return;
          const map: Record<number, PatientReadiness> = {};
          for (const r of results) map[r.patient_id] = r;
          setReadinessByPatient(map);
        },
      );
    });
    return () => {
      cancelled = true;
    };
  }, [day]);

  const isToday = day === TODAY_ISO;
  const dayLabel = formatDate(new Date(`${day}T12:00:00`).toISOString());

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {isToday ? "Today" : dayLabel}
          </h1>
          {!isToday && (
            <p className="text-sm text-slate-500">{day}</p>
          )}
        </div>
        <Link
          to={`/schedule?day=${day}`}
          className="inline-flex items-center px-4 py-2 rounded-md bg-slate-900 text-white text-sm font-medium hover:bg-slate-800"
        >
          + Schedule appointment
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setDay(shiftDay(day, -1))}
          className="px-3 py-1.5 rounded-md border border-slate-200 bg-white text-sm hover:bg-slate-50"
        >
          ← Previous
        </button>
        <button
          type="button"
          onClick={() => setDay(TODAY_ISO)}
          disabled={isToday}
          className="px-3 py-1.5 rounded-md border border-slate-200 bg-white text-sm hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Today
        </button>
        <button
          type="button"
          onClick={() => setDay(shiftDay(day, 1))}
          className="px-3 py-1.5 rounded-md border border-slate-200 bg-white text-sm hover:bg-slate-50"
        >
          Next →
        </button>
      </div>

      {appointments === null ? (
        <p className="text-slate-500">Loading…</p>
      ) : appointments.length === 0 ? (
        <p className="text-slate-500">No appointments on this day.</p>
      ) : (
        <ul className="rounded-lg border border-slate-200 bg-white divide-y divide-slate-200">
          {appointments.map((a) => {
            const readiness = readinessByPatient[a.patient_id] ?? null;
            const subtitle =
              a.status === "CONFIRMED"
                ? "Confirmed"
                : a.status === "CANCELLED"
                  ? "Cancelled"
                  : "Scheduled — needs confirmation";
            return (
              <li key={a.id}>
                <Link
                  to={`/appointments/${a.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-slate-50"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-20 text-sm font-medium tabular-nums text-slate-700">
                      {formatTime(a.starts_at)}
                    </div>
                    <div>
                      <div className="font-medium text-slate-900">
                        {a.patient_name}
                      </div>
                      <div className="text-xs text-slate-500">{subtitle}</div>
                    </div>
                  </div>
                  <ReadyBadge readiness={readiness} />
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
