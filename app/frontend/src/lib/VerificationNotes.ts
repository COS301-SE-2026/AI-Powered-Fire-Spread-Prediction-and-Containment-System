import { ReportStatus } from "../types/Report";

const REASONS: Record<string, string> = {
  missing_required_field: 'Missing required information',
  invalid_location: 'Invalid or missing location',
  outside_boundary: 'Outside service area',
  invalid_timestamp: 'Invalid Timestamp',
  missing_photo: 'No photo attached',
  duplicate_submission: "Duplicate of reporter's own recent report",
  abnormal_rate: 'Unusually high submission rate',
  duplicate_photo: "Photo matches another user's report",
  corroborated_and_trusted: 'Confirmed by multiple independent reports',
  insufficient_signal_for_auto_decision: 'Awaiting more evidence',
  needs_manual_review: 'Location check unavailable',
  manual_review: 'Location check unavailable',
};

const DECISION_LABELS: Record<string, string> = {
  auto_reject: 'Auto-rejected',
  auto_verify: 'Auto-verified',
  manual_review: 'Manual review',
};

const MATCHING_DECISION: Partial<Record<ReportStatus, string>> = {
  verified: 'auto_verify',
  rejected: 'auto_reject',
};

function describeAutoDecision(notes: string): string{
  const separatorIndex = notes.indexOf(': ');
  if (separatorIndex === -1) {
    return DECISION_LABELS[notes] ?? notes;
  }

  const decisionLabel = DECISION_LABELS[getDecision(notes)];
  if (!decisionLabel) {
    return notes;
  }

  const reasonCode = notes.slice(separatorIndex + 2) ;
  const reasonLabel = REASONS[reasonCode] ?? reasonCode.replaceAll('_', ' ');
  return `${decisionLabel} - ${reasonLabel}`;
}

function getDecision(notes: string): string {
  const separatorIndex = notes.indexOf(': ');
  if (separatorIndex === -1) {
    return notes;
  }
  return notes. slice(0, separatorIndex);
}

export function VerificationNotes(notes: string | null | undefined, status: ReportStatus ): string {
  const isFinal = status === 'verified' || status === 'rejected';
  if (!notes) {
    if (isFinal) {
      return 'No automated check recorded';
    }
    return 'Not yet verified';
  }
  
  const autoDecision = describeAutoDecision(notes);

  if (isFinal && MATCHING_DECISION[status] !== getDecision(notes)) {
    return `Manually ${status}`;
  }

  return autoDecision;
}
