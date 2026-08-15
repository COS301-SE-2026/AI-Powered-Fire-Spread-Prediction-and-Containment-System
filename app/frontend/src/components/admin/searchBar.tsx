import React from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
    readonly value: string;
    readonly onChange: (value: string) => void;
    readonly placeholder?: string;
}

export function SearchBar({value, onChange, placeholder ="Search..."}: SearchBarProps) {
  return <div className="input border border-torch/30 rounded-xl focus-within:outline-ignite focus-within:border-none ">
            <Search className="h-[1em] opacity-50" aria-hidden="true"/>
            <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
        </div>
}

