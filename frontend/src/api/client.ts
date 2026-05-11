import type {
  AppointmentWithPatient,
  Confirmability,
  ConfirmFailure,
  Patient,
  PatientReadiness,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body);
  }
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  status: number;
  body: string;
  constructor(status: number, body: string) {
    super(`HTTP ${status}: ${body}`);
    this.status = status;
    this.body = body;
  }
  parsed<T>(): T | null {
    try {
      return JSON.parse(this.body) as T;
    } catch {
      return null;
    }
  }
}

export function listAppointments(): Promise<AppointmentWithPatient[]> {
  return request("/api/appointments");
}

export function getAppointment(id: number): Promise<AppointmentWithPatient> {
  return request(`/api/appointments/${id}`);
}

export function getConfirmability(appointmentId: number): Promise<Confirmability> {
  return request(`/api/appointments/${appointmentId}/confirmability`);
}

export function confirmAppointment(
  appointmentId: number,
): Promise<AppointmentWithPatient> {
  return request(`/api/appointments/${appointmentId}/confirm`, { method: "POST" });
}

export function getPatient(id: number): Promise<Patient> {
  return request(`/api/patients/${id}`);
}

export function getPatientReadiness(id: number): Promise<PatientReadiness> {
  return request(`/api/patients/${id}/readiness`);
}

export type { ConfirmFailure };
