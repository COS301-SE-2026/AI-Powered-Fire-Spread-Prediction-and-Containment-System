export interface ContainmentLines {
    id: string;
    fire_report_id: string;
    line_geom: string;
    drawn_at: string;
}

export interface ContainmentLinesList{
    data: ContainmentLines[];
    total: number;
}

export interface CreateContainmentLine{
    wkt: string;
}