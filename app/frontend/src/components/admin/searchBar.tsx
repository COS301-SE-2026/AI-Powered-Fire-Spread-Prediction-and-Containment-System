import React from "react";

interface SearchBarProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
}

export function SearchBar({value, onChange, placeholder ="Search..."}: SearchBarProps){
    return (
        <div className="flex items-center gap-2">
            <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="w-64 h-9 px-3 text-sm rounded-lg bg-carbon-input border border-carbon-stroke text-neutral placeholder-neutral/30 focus:outline-none focus:border-ignite/50 transition-colors"/>
            <button className="h-9 px-4 text-xs font-semibold font-display tracking-widest uppercase rounded-lg bg-ignite/20 text-flare border border-ignite/30 hover:bg-ignite/30 transition-colors">Search</button>
        </div>
    );
}