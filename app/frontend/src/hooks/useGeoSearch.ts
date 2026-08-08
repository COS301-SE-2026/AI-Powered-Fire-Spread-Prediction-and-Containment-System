// hooks/shared/useGeocodingSuggestions.ts
import { useEffect, useState } from 'react';
import { useDebounce } from './useDebounce';

export interface GeocodingSuggestion {
  readonly place_name: string;
  readonly center: [number, number];
}

async function fetchSuggestions(query: string): Promise<GeocodingSuggestion[]> {
  const res = await fetch(
    `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&autocomplete=true&limit=5&types=address,place,locality,neighborhood,poi`
  );

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

export function useGeoSearch(query: string) {
  const debouncedQuery = useDebounce(query, 300);
  const [suggestions, setSuggestions] = useState<GeocodingSuggestion[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  useEffect(() => {
    if (debouncedQuery.trim().length < 3) {
      setSuggestions([]);
      return;
    }

    let cancelled = false;

    const run = async () => {
      setIsSearching(true);
      setSearchError(null);
      try {
        const results = await fetchSuggestions(debouncedQuery);
        if (cancelled) return;
        setSuggestions(results);
      } catch {
        if (cancelled) return;
        setSuggestions([]);
        setSearchError('Search failed. Please try again.');
      } finally {
        if (!cancelled) setIsSearching(false);
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  return { suggestions, isSearching, searchError };
}