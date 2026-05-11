import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getPatientReadiness, listAppointments } from "../api/client";
import type { AppointmentWithPatient, PatientReadiness } from "../api/types";
import { ReadyBadge } from "../components/ReadyBadge";
import { formatDate, formatTime } from "../lib/format";

export default function DayView() {
  const [appointments, setAppointments] = useState<AppointmentWithPatient[] | null>(
    null,
  );
  const [readinessByPatient, setReadinessByPatient] = useState<
    Record<number, PatientReadiness>
  >({});

  useEffect(() => {
    let cancelled = false;
    listAppointments().then((appts) => {
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
  }, []);

  if (appointments === null) {
    return <div className="text-slate-500">Loading…</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Today</h1>
        <p className="text-sm text-slate-500">
          {formatDate(new Date().toISOString())}
        </p>
      </div>

      {appointments.length === 0 ? (
        <p className="text-slate-500">No appointments today.</p>
      ) : (
        <ul className="rounded-lg border border-slate-200 bg-white divide-y divide-slate-200">
          {appointments.map((a) => {
            const readiness = readinessByPatient[a.patient_id] ?? null;
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
                      <div className="text-xs text-slate-500">
                        {a.status === "CONFIRMED"
                          ? "Confirmed"
                          : "Scheduled — needs confirmation"}
                      </div>
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
