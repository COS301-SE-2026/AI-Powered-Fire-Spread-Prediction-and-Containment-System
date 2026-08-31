const REASONS: Record<string, string> = {
  missing_required_field: 'Missing required information',
  invalid_location: 'Invalid or missing location',
  outside_boundary: 'Outside service area',
  invalid_timestamp: 'Timestamp are invalid',
  missing_photo: 'No photo attatched',
  duplicate_submission: 'Duplicate of your own recent report',
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

export function VerificationNotes(notes: string | null | undefined): string {
  if (!notes) {
    return 'Not yet verified';
  }

  const [decisionPart, reasonPart] = notes.split(': ');
  const decisionLabel = DECISION_LABELS[decisionPart];
  const reasonLabel = reasonPart ? REASONS[reasonPart] : undefined;

  if (!decisionLabel) {
    return notes;
  }

  return reasonLabel ? `${decisionLabel} - ${reasonLabel}` : decisionLabel;
}
