"use client";

import React, { useCallback, useEffect, useRef, useState, useId } from "react";
import { FormError } from "./ReportFormError";
import { MapPin } from "lucide-react";
import { LOCATION_PLACEHOLDER } from "./Reportdetailsform";

interface GeocodingSuggestion {
    readonly place_name: string;
    readonly center: [number, number];
}

interface LocationSelection {
    readonly lat: number;
    readonly lng: number;
    readonly address: string;
}

interface LocationFieldProps {
    readonly value: string;
    readonly error?: string;
    readonly onChange: (value: string) => void;
    readonly onValidSelect: (loc: LocationSelection) => void;
}

interface SuggestionRowProps {
    readonly suggestion: GeocodingSuggestion;
    readonly onSelect: (s: GeocodingSuggestion) => void;
}

function SuggestionPin() {
    return <MapPin size={12} className="mt-0.5 shrink-0 text-ignite/70" />;
}

function SuggestionRow({ suggestion, onSelect }: SuggestionRowProps) {
    return (
        <li>
            <button type="button" onMouseDown={(e) => { e.preventDefault(); onSelect(suggestion)}} className="flex items-start gap-2.5">
                <SuggestionPin />
                <span className="leading-snug">{suggestion.place_name}</span>
            </button>
        </li>
    );
}

function renderSuggestions( suggestions: GeocodingSuggestion[], onSelect: (s: GeocodingSuggestion) => void): React.ReactNode[] {
    const rows: React.ReactNode[] = [];
    for (const s of suggestions) {
        rows.push(<SuggestionRow key={s.place_name} suggestion={s} onSelect={onSelect} />);
    }
    return rows;
}

async function fetchSuggestions(query: string): Promise<GeocodingSuggestion[]> {
    const res = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&autocomplete=true&limit=5&types=address,place,locality,neighborhood,poi`);

    if (!res.ok) {
        throw new Error(`Geocoding request failed: ${res.status} ${res.statusText}`);
    }

    const json = await res.json();
    const features = json.features ?? [];
    const results: GeocodingSuggestion[] = [];
    for (const f of features) {
        results.push({ place_name: f.place_name, center: f.center });
    }
    return results;
}

function handleClick(e: React.MouseEvent<HTMLInputElement>) {
    e.currentTarget.select();
}

export function LocationField({ value, error, onChange, onValidSelect}: LocationFieldProps) {
    const id = useId();
    const errorId = error ? `${id}-error` : undefined;

    const [suggestions, setSuggestions] = useState<GeocodingSuggestion[]>([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);
    const [searchError, setSearchError] = useState<string | null>(null);


    useEffect(() => {
        function handleOutside(e: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
                setShowDropdown(false);
            }
        }
        document.addEventListener("mousedown", handleOutside);
        return () => document.removeEventListener("mousedown", handleOutside);
    }, []);

    const runSearch = useCallback(async (query: string) => {
        if (query.trim().length < 3) {
            setSuggestions([]);
            setShowDropdown(false);
            return;
        }
        setIsSearching(true);
        setSearchError(null);
        try {
            const results = await fetchSuggestions(query);
            setSuggestions(results);
            setShowDropdown(results.length > 0);
        } catch {
            setSuggestions([]);
            setSearchError("Search failed. Please try again.");
        } finally {
            setIsSearching(false);
        }
    }, []);

    function handleFocus(e: React.FocusEvent<HTMLInputElement>) {
        if (value === LOCATION_PLACEHOLDER) {
            onChange("");
        }
    }

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        const val = e.target.value;

        onChange(val);

        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => runSearch(val), 300);
    }

    function handleSuggestionSelect(s: GeocodingSuggestion) {
        setSuggestions([]);
        setShowDropdown(false);
        onValidSelect({ lat: s.center[1], lng: s.center[0], address: s.place_name });
    }
    return (
        <div className="dropdown w-full" ref={wrapperRef}>
            <span className="label-text font-semibold mb-2 block">Location</span>
            <div className="input input-bordered w-full flex item-center gap-2  bg-surface-input border-carbon-stroke focus-within:outline-ignite focus-within:border-none h-11">
                <input id={id} type="text" value={value} onChange={handleInputChange} onFocus={handleFocus} onClick={handleClick} placeholder="Drop a pin or type your address" className="grow bg-transparent focus:outline-none" aria-invalid={!!error} aria-describedby={errorId}/>
                {isSearching && <span className="loading loading-spinner loading-xs text-ignite" />}
            </div>

            {showDropdown && suggestions.length > 0 && (
                <ul className = "menu dropdown-content absolute top-full left-0 right-0 mt-1 z-50 bg-surface-elevated border border-white/15">
                    {renderSuggestions(suggestions, handleSuggestionSelect)}
                </ul>
            )}
            {error && <FormError message={error} id={errorId} />}
            {searchError && <span className="text-error text-xs mt-1">{searchError}</span>}
        </div>
    );
}