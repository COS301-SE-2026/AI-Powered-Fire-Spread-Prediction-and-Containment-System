import React from 'react';
import { GeocodingSuggestion } from '../../hooks/useGeoSearch';
import { SuggestionPin } from './SuggestionPin';

interface SuggestionRowProps {
    readonly suggestion: GeocodingSuggestion;
    readonly onSelect: (s: GeocodingSuggestion) => void;
}

export function SuggestionRow({ suggestion, onSelect }: SuggestionRowProps) {
  return <li>
            <button type="button" onMouseDown={(e) => { e.preventDefault(); onSelect(suggestion)}} className="flex items-start gap-2.5">
                <SuggestionPin />
                <span className="leading-snug">{suggestion.place_name}</span>
            </button>
        </li>
}