import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import {
  ApiError,
  createAppointment,
  listPatients,
} from "../api/client";
import type {
  Patient,
  ReadinessIssue,
  ScheduleFailure,
} from "../api/types";

function defaultDay(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${dd}`;
}

export default function SchedulePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const initialDay = params.get("day") ?? defaultDay();

  const [patients, setPatients] = useState<Patient[] | null>(null);
  const [patientId, setPatientId] = useState<string>("");
  const [day, setDay] = useState<string>(initialDay);
  const [time, setTime] = useState<string>("09:00");
  const [submitting, setSubmitting] = useState(false);
  const [issues, setIssues] = useState<ReadinessIssue[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listPatients().then(setPatients);
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!patientId) {
      setError("Pick a patient.");
      return;
    }
    setSubmitting(true);
    setIssues(null);
    setError(null);
    const startsAt = `${day}T${time}:00`;
    try {
      const appt = await createAppointment({
        patient_id: Number(patientId),
        starts_at: startsAt,
      });
      navigate(`/appointments/${appt.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        const parsed = err.parsed<ScheduleFailure>();
        setIssues(parsed?.detail.issues ?? []);
      } else if (err instanceof ApiError && err.status === 404) {
        setError("Patient not found.");
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to={`/?day=${day}`} className="text-sm text-slate-500 hover:text-slate-700">
          ← Back
        </Link>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          New appointment
        </div>
        <h1 className="text-xl font-semibold">Schedule appointment</h1>
        <p className="text-sm text-slate-500 mt-1">
          The patient must pass readiness checks before they can be scheduled.
        </p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="patient" className="block text-sm font-medium text-slate-700">
              Patient
            </label>
            <select
              id="patient"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
              disabled={patients === null}
            >
              <option value="">
                {patients === null ? "Loading…" : "Select a patient…"}
              </option>
              {patients?.map((p) => (
                <option key={p.id} value={String(p.id)}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="day" className="block text-sm font-medium text-slate-700">
                Date
              </label>
              <input
                id="day"
                type="date"
                value={day}
                onChange={(e) => setDay(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="time" className="block text-sm font-medium text-slate-700">
                Time
              </label>
              <input
                id="time"
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting || patients === null}
              className="inline-flex items-center px-4 py-2 rounded-md bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 disabled:opacity-50"
            >
              {submitting ? "Scheduling…" : "Schedule"}
            </button>
          </div>

          {issues !== null && issues.length > 0 && (
            <div className="space-y-2 pt-2">
              <div className="text-sm font-medium text-amber-900">
                Patient is not ready to be scheduled:
              </div>
              <ul className="space-y-2">
                {issues.map((i) => (
                  <li
                    key={i.type}
                    className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2"
                  >
                    <div className="text-sm font-medium text-amber-900">{i.type}</div>
                    <div className="text-sm text-amber-800">{i.message}</div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {error !== null && (
            <div className="text-sm text-rose-700 pt-2">{error}</div>
          )}
        </form>
      </div>
    </div>
  );
}
