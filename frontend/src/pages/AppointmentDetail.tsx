import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getAppointment, getPatientReadiness } from "../api/client";
import type { AppointmentWithPatient, PatientReadiness } from "../api/types";
import { ConfirmButton } from "../components/ConfirmButton";
import { ReadyBadge } from "../components/ReadyBadge";
import { formatDate, formatTime } from "../lib/format";

export default function AppointmentDetail() {
  const { id } = useParams<{ id: string }>();
  const appointmentId = Number(id);

  const [appointment, setAppointment] = useState<AppointmentWithPatient | null>(null);
  const [readiness, setReadiness] = useState<PatientReadiness | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    if (!Number.isFinite(appointmentId)) return;

    getAppointment(appointmentId).then((appt) => {
      if (cancelled) return;
      setAppointment(appt);
      return getPatientReadiness(appt.patient_id).then((r) => {
        if (cancelled) return;
        setReadiness(r);
      });
    });
    return () => {
      cancelled = true;
    };
  }, [appointmentId, reloadKey]);

  if (appointment === null) {
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
              Appointment
            </div>
            <div className="text-xl font-semibold mt-1">
              {appointment.patient_name}
            </div>
            <div className="text-sm text-slate-500 mt-1">
              {formatDate(appointment.starts_at)} at{" "}
              {formatTime(appointment.starts_at)} · with{" "}
              {appointment.provider_name}
            </div>
          </div>
          <ReadyBadge readiness={readiness} />
        </div>

        <div className="text-sm">
          <Link
            to={`/patients/${appointment.patient_id}`}
            className="text-slate-600 underline hover:text-slate-800"
          >
            View patient
          </Link>
        </div>

        <div className="pt-2 border-t border-slate-100">
          <ConfirmButton
            appointmentId={appointment.id}
            status={appointment.status}
            onConfirmed={() => setReloadKey((k) => k + 1)}
          />
        </div>
      </div>
    </div>
  );
}
