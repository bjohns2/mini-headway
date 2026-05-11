import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getPatient, getPatientReadiness } from "../api/client";
import type { Patient, PatientReadiness } from "../api/types";
import { ReadyBadge } from "../components/ReadyBadge";

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>();
  const patientId = Number(id);

  const [patient, setPatient] = useState<Patient | null>(null);
  const [readiness, setReadiness] = useState<PatientReadiness | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!Number.isFinite(patientId)) return;
    Promise.all([getPatient(patientId), getPatientReadiness(patientId)]).then(
      ([p, r]) => {
        if (cancelled) return;
        setPatient(p);
        setReadiness(r);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  if (patient === null) {
    return <div className="text-slate-500">Loading…</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-sm text-slate-500 hover:text-slate-700">
          ← Back to today
        </Link>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-500">
              Patient
            </div>
            <div className="text-xl font-semibold mt-1">{patient.name}</div>
            <div className="text-sm text-slate-500 mt-1">
              DOB {patient.date_of_birth}
            </div>
          </div>
          <ReadyBadge readiness={readiness} />
        </div>

        <div className="pt-2 border-t border-slate-100">
          <h2 className="text-sm font-medium text-slate-700 mb-2">
            Readiness issues
          </h2>
          {readiness === null ? (
            <div className="text-sm text-slate-500">Loading…</div>
          ) : readiness.issues.length === 0 ? (
            <div className="text-sm text-slate-500">No issues.</div>
          ) : (
            <ul className="space-y-2">
              {readiness.issues.map((issue) => (
                <li
                  key={issue.type}
                  className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2"
                >
                  <div className="text-sm font-medium text-amber-900">
                    {issue.type}
                  </div>
                  <div className="text-sm text-amber-800">{issue.message}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
