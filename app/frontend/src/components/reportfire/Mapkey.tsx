import React from "react";

export default function MapKey() {
    return (
        <div 
            className="flex items-center gap-6 px-4 py-2 text-xs flex-wrap font-body text-neutral/45 bg-carbon-side border-t border-carbon-stroke"
            style={{ borderTopWidth: '1px' }}
        >
            {/* Active burn area */}
            <span className="flex items-center gap-2">
                <span
                    className="inline-block w-8 h-3 rounded-sm shrink-0 border border-ignite bg-ignite/12"
                    style={{ borderWidth: '1.5px' }}
                />
                Active burn area
            </span>

            {/* Fire boundary */}
            <span className="flex items-center gap-2">
                <span
                    className="inline-block w-8 h-3 rounded-sm shrink-0 border border-dashed border-ignite opacity-60"
                    style={{ borderWidth: '1.5px' }}
                />
                Fire boundary (drag to size)
            </span>

            {/* Drag handle */}
            <span className="flex items-center gap-1.5">
                <span className="text-base leading-none font-light font-mono text-neutral/70">
                    +
                </span>
                Drag handle
            </span>
        </div>
    );
}