"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Paperclip, Check, AlertTriangle } from "lucide-react";

export type ReportFormData = {
    location: string;
    description: string;
    photo: File | null;
};

interface GeocodingSuggestion {
    place_name: string;
    center: [number, number];
}

type Props = {
    location?: string;
    onSubmit?: (data: ReportFormData) => void;
    onLocationSearch?: (loc: { lat: number; lng: number; address: string }) => void;
};

const baseInput =
    "w-full bg-white/10 border rounded-md text-sm text-white placeholder-white/30 focus:outline-none focus:border-ignite focus:bg-white/15 transition-colors";

export default function ReportDetailsForm({ location = "", onSubmit, onLocationSearch }: Props) {
    const [editableLocation, setEditableLocation] = useState(location);
    const [description, setDescription] = useState("");
    const [photo, setPhoto] = useState<File | null>(null);
    const [errors, setErrors] = useState<{ location?: string; photo?: string }>({});
    const fileRef = useRef<HTMLInputElement>(null);

    const [suggestions, setSuggestions] = useState<GeocodingSuggestion[]>([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);
    const skipFetchRef = useRef(false);
    // True only when location came from a map click or autocomplete selection
    const validLocationRef = useRef(false);

    useEffect(() => {
        if (location && location !== "Click the map to drop a pin") {
            skipFetchRef.current = true;
            validLocationRef.current = true;
            setEditableLocation(location);
            setShowDropdown(false);
            setErrors((prev) => ({ ...prev, location: undefined }));
        }
    }, [location]);

    useEffect(() => {
        function handleOutside(e: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
                setShowDropdown(false);
            }
        }
        document.addEventListener("mousedown", handleOutside);
        return () => document.removeEventListener("mousedown", handleOutside);
    }, []);

    const fetchSuggestions = useCallback(async (query: string) => {
        if (query.trim().length < 3) {
            setSuggestions([]);
            setShowDropdown(false);
            return;
        }
        setIsSearching(true);
        try {
            const res = await fetch(
                `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json` +
                `?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&autocomplete=true&limit=5&types=address,place,locality,neighborhood,poi`
            );
            const json = await res.json();
            const results: GeocodingSuggestion[] = (json.features ?? []).map((f: any) => ({
                place_name: f.place_name,
                center: f.center,
            }));
            setSuggestions(results);
            setShowDropdown(results.length > 0);
        } catch {
            setSuggestions([]);
        } finally {
            setIsSearching(false);
        }
    }, []);

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        const val = e.target.value;
        setEditableLocation(val);
        validLocationRef.current = false; // typing invalidates any previous selection
        if (val.trim()) setErrors((prev) => ({ ...prev, location: undefined }));
        if (skipFetchRef.current) { skipFetchRef.current = false; return; }
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => fetchSuggestions(val), 300);
    }

    function handleSuggestionSelect(s: GeocodingSuggestion) {
        skipFetchRef.current = true;
        validLocationRef.current = true;
        setEditableLocation(s.place_name);
        setSuggestions([]);
        setShowDropdown(false);
        setErrors((prev) => ({ ...prev, location: undefined }));
        onLocationSearch?.({ lat: s.center[1], lng: s.center[0], address: s.place_name });
    }

    function reset() {
        setEditableLocation("Click the map to drop a pin");
        setDescription("");
        photo && setPhoto(null);
        setErrors({});
        if (fileRef.current) fileRef.current.value = "";
    }

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        const newErrors: { location?: string; photo?: string } = {};

        if (!validLocationRef.current || !editableLocation.trim() || editableLocation === "Click the map to drop a pin") {
            newErrors.location = "Please select a valid location from the map or search suggestions.";
        }

        const isDesktop = typeof window !== "undefined" && window.innerWidth >= 768;
        if (isDesktop && !photo) {
            newErrors.photo = "Field evidence attachment is mandatory on desktop. Please upload a telemetry image.";
        }

        if (Object.keys(newErrors).length > 0) { setErrors(newErrors); return; }

        setErrors({});
        onSubmit?.({ location: editableLocation, description, photo });
        reset();
    }

    function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0] ?? null;
        if (file) {
            if (!file.type.startsWith("image/")) {
                setErrors((prev) => ({ ...prev, photo: "Invalid file type. Only image files (PNG, JPG, WEBP) are permitted." }));
                setPhoto(null);
                if (fileRef.current) fileRef.current.value = "";
                return;
            }
            setPhoto(file);
            setErrors((prev) => ({ ...prev, photo: undefined }));
        }
    }

    return (
        <form onSubmit={handleSubmit} className="w-full flex flex-col font-body">

            <h2
                className="text-xl font-bold mb-4"
                style={{ fontFamily: "var(--font-display)", color: "var(--color-primary-content)" }}
            >
                Report details
            </h2>

            <div className="flex flex-col gap-5">

                {/* Location — full width input, no side button */}
                <div className="flex flex-col gap-1.5" ref={wrapperRef}>
                    <label className="text-sm font-semibold text-white">Location</label>
                    <div className="relative">
                        <input
                            type="text"
                            value={editableLocation}
                            onChange={handleInputChange}
                            onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
                            placeholder="Drop a pin or type your address"
                            className={`${baseInput} h-11 px-3 ${
                                errors.location ? "border-error/60 focus:border-error" : "border-white/20"
                            }`}
                        />
                        {isSearching && (
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                <div className="w-3.5 h-3.5 border-2 border-ignite/40 border-t-ignite rounded-full animate-spin" />
                            </div>
                        )}

                        {/* Autocomplete dropdown */}
                        {showDropdown && suggestions.length > 0 && (
                            <div className="absolute top-full left-0 right-0 mt-1 z-50 rounded-md border border-white/15 bg-[#1a1a1a] shadow-2xl overflow-hidden">
                                {suggestions.map((s, i) => (
                                    <button
                                        key={i}
                                        type="button"
                                        onMouseDown={() => handleSuggestionSelect(s)}
                                        className="w-full text-left px-3 py-2.5 text-sm text-white/70 hover:bg-white/10 hover:text-white flex items-start gap-2.5 transition-colors border-b border-white/5 last:border-0"
                                    >
                                        <svg className="mt-0.5 flex-shrink-0 text-ignite/70" width="11" height="13" viewBox="0 0 12 14" fill="none">
                                            <path d="M6 0C3.24 0 1 2.24 1 5c0 3.75 5 9 5 9s5-5.25 5-9c0-2.76-2.24-5-5-5z" fill="currentColor"/>
                                            <circle cx="6" cy="5" r="2" fill="white" fillOpacity="0.8"/>
                                        </svg>
                                        <span className="leading-snug">{s.place_name}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    {errors.location && (
                        <div className="flex items-center gap-1.5 text-error text-xs font-medium mt-0.5">
                            <AlertTriangle size={13} />
                            <span>{errors.location}</span>
                        </div>
                    )}
                </div>

                {/* Description */}
                <div className="flex flex-col gap-1.5">
                    <label className="flex items-baseline gap-2">
                        <span className="text-sm font-semibold text-white">Description</span>
                        <span className="text-xs text-white/40">optional</span>
                    </label>
                    <textarea
                        rows={4}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="E.g., Surface line fire spreading northeast toward residential properties..."
                        className={`${baseInput} border-white/20 p-3 leading-relaxed resize-none text-sm`}
                    />
                </div>

                {/* Attach Evidence */}
                <div className="hidden md:flex md:flex-col gap-1.5">
                    <label className="text-sm font-semibold text-white">Attach Evidence</label>
                    <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handlePhotoChange} />
                    <button
                        type="button"
                        onClick={() => fileRef.current?.click()}
                        className={`h-11 w-full flex items-center justify-center gap-2 rounded-md border text-sm transition-colors duration-150 ${
                            photo
                                ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                                : errors.photo
                                ? "bg-error/10 border-dashed border-error/50 text-error/80 hover:bg-error/15"
                                : "bg-white/5 border-dashed border-white/20 text-white/50 hover:bg-white/10 hover:text-white/80"
                        }`}
                    >
                        {photo ? (
                            <><Check size={14} strokeWidth={2.5} /><span className="truncate max-w-[200px] font-mono text-xs">{photo.name}</span></>
                        ) : (
                            <><Paperclip size={14} /><span>Attach Image</span></>
                        )}
                    </button>
                    {errors.photo && (
                        <div className="flex items-center gap-1.5 text-error text-xs font-medium mt-0.5">
                            <AlertTriangle size={13} />
                            <span>{errors.photo}</span>
                        </div>
                    )}
                </div>

                {/* Submit */}
                <div className="pt-4 border-t border-white/5 mt-1">
                    <button
                        type="submit"
                        className="w-full h-11 bg-ignite hover:bg-ignite/90 active:scale-[0.98] text-white font-display font-bold tracking-widest uppercase text-sm rounded-md transition-all shadow-lg shadow-ignite/20"
                    >
                        Submit Fire Report
                    </button>
                </div>

            </div>
        </form>
    );
}