// components/MapKey.tsx
// ─────────────────────────────────────────────────────────────
// Legend bar below the map. Purely presentational — no props.
// ─────────────────────────────────────────────────────────────

export default function MapKey() {
  return (
    <div
      className="flex items-center gap-6 px-4 py-2 text-xs flex-wrap"
      style={{
        background: "var(--color-carbon-side)",
        borderTop: "1px solid rgba(255,255,255,0.08)",
        color: "rgba(255,255,255,0.45)",
        fontFamily: "var(--font-body)",
      }}
    >
      {/* Active burn area */}
      <span className="flex items-center gap-2">
        <span
          className="inline-block w-8 h-3 rounded-sm shrink-0"
          style={{
            background: "rgba(232, 69, 0, 0.12)",
            border: "1.5px solid var(--color-ignite)",
          }}
        />
        Active burn area
      </span>

      {/* Fire boundary */}
      <span className="flex items-center gap-2">
        <span
          className="inline-block w-8 h-3 rounded-sm shrink-0"
          style={{ border: "1.5px dashed var(--color-ignite)", opacity: 0.6 }}
        />
        Fire boundary (drag to size)
      </span>

      {/* Drag handle */}
      <span className="flex items-center gap-1.5">
        <span
          className="text-base leading-none font-light"
          style={{ color: "rgba(255,255,255,0.7)" }}
        >
          +
        </span>
        Drag handle
      </span>
    </div>
  );
}