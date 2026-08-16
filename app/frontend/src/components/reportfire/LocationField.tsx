'use client';

import React, { useEffect, useRef, useState, useId } from 'react';
import { Alert } from '../shared/Alerts';
import { LOCATION_PLACEHOLDER } from './locationConstants';
import { GeocodingSuggestion, useGeoSearch } from '../../hooks/useGeoSearch';
import { SuggestionRow } from './SuggestionRow';

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

function renderSuggestions(
  suggestions: GeocodingSuggestion[],
  onSelect: (s: GeocodingSuggestion) => void
): React.ReactNode[] {
  const rows: React.ReactNode[] = [];
  for (const s of suggestions) {
    rows.push(<SuggestionRow key={s.place_name} suggestion={s} onSelect={onSelect} />);
  }
  return rows;
}

function handleClick(e: React.MouseEvent<HTMLInputElement>) {
  e.currentTarget.select();
}

export function LocationField({ value, error = '', onChange, onValidSelect }: LocationFieldProps) {
  const id = useId();
  const errorId = error ? `${id}-error` : undefined;

  const { suggestions, isSearching, searchError } = useGeoSearch(value);
  const [dismissed, setDismissed] = useState(false);
  const [prevValue, setPrevValue] = useState(value);
  const wrapperRef = useRef<HTMLDivElement>(null);

  if (value !== prevValue) {
    setPrevValue(value);
    if (dismissed) setDismissed(false);
  }

  const showDropdown = suggestions.length > 0 && !dismissed;

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setDismissed(false);
      }
    }
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  function handleFocus(e: React.FocusEvent<HTMLInputElement>) {
    if (value === LOCATION_PLACEHOLDER) {
      onChange('');
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    onChange(e.target.value);
  }

  function handleSuggestionSelect(s: GeocodingSuggestion) {
    setDismissed(true);
    onValidSelect({ lat: s.center[1], lng: s.center[0], address: s.place_name });
  }
  return (
    <div className="dropdown w-full" ref={wrapperRef}>
      <span className="label-text text-lg font-semibold mb-2 block">Location</span>
      <div className="input input-bordered w-full flex item-center gap-2  bg-surface-input border-carbon-stroke focus-within:outline-ignite focus-within:border-none h-11">
        <input
          id={id}
          type="text"
          value={value}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onClick={handleClick}
          placeholder="Drop a pin or type your address"
          className="grow bg-transparent focus:outline-none"
          aria-invalid={!!error}
          aria-describedby={errorId}
        />
        {isSearching && <span className="loading loading-spinner loading-xs text-ignite" />}
      </div>

      {showDropdown && suggestions.length > 0 && (
        <ul className="menu dropdown-content absolute top-full left-0 right-0 mt-1 z-50 bg-surface-elevated border border-white/15">
          {renderSuggestions(suggestions, handleSuggestionSelect)}
        </ul>
      )}
      {error && <Alert variant="error" message={error} id={errorId} />}
      {searchError && <span className="text-error text-xs mt-1">{searchError}</span>}
    </div>
  );
}
