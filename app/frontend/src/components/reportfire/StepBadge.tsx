import React from "react";

export function StepBadge({ number }: Readonly<{number: number }>) {
  return <span className="w-6 h-6 rounded-full bg-primary grid place-items-center text-primary-content font-bold text-xs leading-none">{number}</span>
}