import React from "react";

interface SearchBarProps {
    readonly value: string;
    readonly onChange: (value: string) => void;
    readonly placeholder?: string;
}

export function SearchBar({value, onChange, placeholder ="Search..."}: SearchBarProps){
    return (
        <div className="flex items-center gap-2">
            <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="w-64 h-9 px-3 text-sm rounded-lg bg-carbon-input border border-carbon-stroke text-neutral placeholder-neutral/30 focus:outline-none focus:border-ignite/50 transition-colors"/>
        </div>
    );
}