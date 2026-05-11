export type AppointmentStatus = "SCHEDULED" | "CONFIRMED" | "CANCELLED";

export interface AppointmentWithPatient {
  id: number;
  patient_id: number;
  provider_id: number;
  starts_at: string;
  status: AppointmentStatus;
  patient_name: string;
  provider_name: string;
}

export type ReadinessIssueType =
  | "MISSING_INSURANCE"
  | "INSURANCE_TERMINATED"
  | "INSURANCE_NOT_VERIFIED";

export interface ReadinessIssue {
  type: ReadinessIssueType;
  message: string;
}

export interface PatientReadiness {
  patient_id: number;
  is_ready: boolean;
  issues: ReadinessIssue[];
}

export type UnconfirmableReasonCode =
  | "PATIENT_MISSING_INSURANCE"
  | "ELIGIBILITY_NOT_CLAIM_READY"
  | "MENTAL_HEALTH_NOT_COVERED"
  | "PROVIDER_LICENSE_EXPIRED";

export interface UnconfirmableBlocker {
  reason: UnconfirmableReasonCode;
  message: string;
}

export interface Confirmability {
  appointment_id: number;
  is_confirmable: boolean;
  blockers: UnconfirmableBlocker[];
}

export interface Patient {
  id: number;
  name: string;
  date_of_birth: string;
}

export interface ConfirmFailure {
  detail: {
    message: string;
    blockers: UnconfirmableBlocker[];
  };
}
