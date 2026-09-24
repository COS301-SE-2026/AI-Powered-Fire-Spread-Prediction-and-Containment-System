export interface ContainmentLine {
  id: string;
  fire_report_id: string;
  line_geom: string;
  drawn_at: string;
}

export interface ContainmentLinesList {
  data: ContainmentLine[];
  total: number;
}

export interface CreateContainmentLine {
  wkt: string;
}

export interface LocalLine {
  localId: string;
  dbId: string | null;
  wkt: string;
  fireReportId: string | null,
  synced: boolean,
}
export interface SuggestedContainmentLine {
  wkt: string;
  length_m: number;
  build_time_min: number;
  arrival_at_line_min: number;
  margin_min: number;
  shielded_cell_score: number;
}

export interface SuggestedContainmentLinesList {
  data: SuggestedContainmentLine[];
  total: number;
}