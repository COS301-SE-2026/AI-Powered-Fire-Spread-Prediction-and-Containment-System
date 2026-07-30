import React from "react";

const spacing = [
    { label: "Small", value: "8px", usage: "Small gaps and grouped controls" },
    { label: "Medium", value: "16px", usage: "Cards and component spacing" },
    { label: "Large", value: "24px", usage: "Page padding and section spacing" },
    { label: "Extra Large", value: "32px", usage: "Space between major sections" },
];

const breakpoints = [
    { name: "md", width: "768px", use: "Forms change to two columns" },
    { name: "lg", width: "1024px", use: "Dashboard grids" },
    { name: "xl", width: "1280px", use: "Main dashboard layout" },
];

const rules = [
    "Use consistent spacing throughout every page.",
    "Keep mobile layouts in a single column whenever possible.",
    "Use cards to group related information.",
    "Use 24px page padding on primary pages.",
    "Avoid unnecessary nested layouts.",
];

export default function LayoutSpacing() {
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>

            <p
                style={{
                    fontFamily: "var(--font-body)",
                    fontSize: "18px",
                    color: "#B0B8C8",
                    maxWidth: "800px",
                    lineHeight: "1.75",
                    fontWeight: 300,
                }}
            >
                Fireaway uses a simple responsive layout with consistent spacing
                to keep information easy to scan during emergency situations.
                The interface follows Tailwind's default spacing scale and a
                small set of responsive breakpoints.
            </p>

            {/* Spacing */}

            <div
                style={{
                    border: "1px solid var(--color-carbon-stroke)",
                    borderRadius: "var(--radius-md)",
                    overflow: "hidden",
                }}
            >
                <div
                    style={{
                        padding: "14px 20px",
                        background: "var(--color-carbon-input)",
                        borderBottom: "1px solid var(--color-carbon-stroke)",
                    }}
                >
                    <p
                        style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "13px",
                            color: "#A0ACC0",
                            fontWeight: 600,
                            letterSpacing: "0.15em",
                            textTransform: "uppercase",
                        }}
                    >
                        Spacing Scale
                    </p>
                </div>

                {spacing.map((item, index) => (
                    <div
                        key={item.label}
                        style={{
                            display: "grid",
                            gridTemplateColumns: "120px 80px 1fr",
                            padding: "16px 20px",
                            background:
                                index % 2 === 0
                                    ? "var(--color-carbon-card)"
                                    : "var(--color-carbon-input)",
                            borderBottom:
                                index !== spacing.length - 1
                                    ? "1px solid var(--color-carbon-stroke)"
                                    : "none",
                        }}
                    >
                        <strong>{item.label}</strong>
                        <span>{item.value}</span>
                        <span>{item.usage}</span>
                    </div>
                ))}
            </div>

            {/* Breakpoints */}

            <div
                style={{
                    border: "1px solid var(--color-carbon-stroke)",
                    borderRadius: "var(--radius-md)",
                    overflow: "hidden",
                }}
            >
                <div
                    style={{
                        padding: "14px 20px",
                        background: "var(--color-carbon-input)",
                        borderBottom: "1px solid var(--color-carbon-stroke)",
                    }}
                >
                    <p
                        style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "13px",
                            color: "#A0ACC0",
                            fontWeight: 600,
                            letterSpacing: "0.15em",
                            textTransform: "uppercase",
                        }}
                    >
                        Responsive Breakpoints
                    </p>
                </div>

                {breakpoints.map((bp, index) => (
                    <div
                        key={bp.name}
                        style={{
                            display: "grid",
                            gridTemplateColumns: "120px 100px 1fr",
                            padding: "16px 20px",
                            background:
                                index % 2 === 0
                                    ? "var(--color-carbon-card)"
                                    : "var(--color-carbon-input)",
                            borderBottom:
                                index !== breakpoints.length - 1
                                    ? "1px solid var(--color-carbon-stroke)"
                                    : "none",
                        }}
                    >
                        <strong>{bp.name}</strong>
                        <span>{bp.width}</span>
                        <span>{bp.use}</span>
                    </div>
                ))}
            </div>
            {/* Layout Rules */}
            <div
                style={{
                    border: "1px solid var(--color-carbon-stroke)",
                    borderRadius: "var(--radius-md)",
                    overflow: "hidden",
                }}
            >
                <div
                    style={{
                        padding: "14px 20px",
                        background: "var(--color-carbon-input)",
                        borderBottom: "1px solid var(--color-carbon-stroke)",
                    }}
                >
                    <p
                        style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "13px",
                            color: "#A0ACC0",
                            fontWeight: 600,
                            letterSpacing: "0.15em",
                            textTransform: "uppercase",
                        }}
                    >
                        Layout Guidelines
                    </p>
                </div>

                <div
                    style={{
                        padding: "24px",
                        display: "flex",
                        flexDirection: "column",
                        gap: "12px",
                        background: "var(--color-carbon-card)",
                    }}
                >
                    {rules.map(rule => (
                        <p
                            key={rule}
                            style={{
                                fontFamily: "var(--font-body)",
                                color: "#A0A8B8",
                                lineHeight: 1.6,
                            }}
                        >
                            • {rule}
                        </p>
                    ))}
                </div>
            </div>

        </div>
    );
}