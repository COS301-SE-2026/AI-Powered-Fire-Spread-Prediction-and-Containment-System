from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

import rasterio
from rasterio.errors import RasterioIOError

from app.backend.ml.features.terrain import DEMREADENV

TILE_TEMPLATE = "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM"


def _tile_name(tile_lat: int, tile_lon: int) -> str:
    ns = "N" if tile_lat >= 0 else "S"
    ew = "E" if tile_lon >= 0 else "W"
    return TILE_TEMPLATE.format(ns=ns, lat=abs(tile_lat), ew=ew, lon=abs(tile_lon))


def _tile_path(tile_lat: int, tile_lon: int) -> str:
    name = _tile_name(tile_lat, tile_lon)
    return f"/vsis3/copernicus-dem-30m/{name}/{name}.tif"


def get_overlapping_tiles(
    min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> list[tuple[int, int]]:
    """Every 1x1 degree (tile_lat, tile_lon) whose tile overlaps the bbox.

    Same floor-based tile addressing as dem_vsis3_path() (a tile at
    integer degree N covers [N, N+1)), just applied across the whole
    range instead of only the bbox center.
    """
    lat0, lat1 = math.floor(min_lat), math.floor(max_lat)
    lon0, lon1 = math.floor(min_lon), math.floor(max_lon)
    # if max is exactly on a tile boundary, don't pull in the next tile
    if max_lat == lat1 and lat1 > lat0:
        lat1 -= 1
    if max_lon == lon1 and lon1 > lon0:
        lon1 -= 1
    return [
        (tile_lat, tile_lon)
        for tile_lat in range(lat0, lat1 + 1)
        for tile_lon in range(lon0, lon1 + 1)
    ]


class _TileInfo:
    __slots__ = (
        "path",
        "left",
        "bottom",
        "right",
        "top",
        "width",
        "height",
        "crs",
        "dtype",
        "nodata",
    )

    def __init__(self, path, bounds, width, height, crs, dtype, nodata):
        self.path = path
        self.left, self.bottom, self.right, self.top = bounds
        self.width, self.height = width, height
        self.crs, self.dtype, self.nodata = crs, dtype, nodata


def _probe_tiles(tiles: list[tuple[int, int]]) -> list[_TileInfo]:
    """Open each candidate tile remotely to confirm it exists and read its
    real georeferencing. Some tiles (open ocean) legitimately don't exist
    in the Copernicus DEM archive — those are skipped with a warning
    rather than failing the whole mosaic.
    """
    infos: list[_TileInfo] = []
    with rasterio.Env(**DEMREADENV):
        for tile_lat, tile_lon in tiles:
            path = _tile_path(tile_lat, tile_lon)
            try:
                with rasterio.open(path) as src:
                    infos.append(
                        _TileInfo(
                            path=path,
                            bounds=src.bounds,
                            width=src.width,
                            height=src.height,
                            crs=src.crs,
                            dtype=src.dtypes[0],
                            nodata=src.nodata,
                        )
                    )
            except RasterioIOError:
                print(f"WARNING: tile not found, skipping: {path}")
    if not infos:
        raise RuntimeError("No DEM tiles found for the requested bbox — check bounds.")
    return infos


def build_dem_vrt(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    out_path: str,
) -> Path:
    """Builds a seamless VRT mosaic over [min_lon, min_lat, max_lon, max_lat]
    from Copernicus DEM GLO-30 tiles on AWS Open Data, writing the VRT XML
    by hand (no osgeo.gdal, no gdalbuildvrt CLI).
    """
    tiles = get_overlapping_tiles(min_lon, min_lat, max_lon, max_lat)
    print(f"Probing {len(tiles)} candidate DEM tiles...")
    infos = _probe_tiles(tiles)
    print(f"{len(infos)}/{len(tiles)} tiles exist and were opened")

    # Shared output grid: finest available pixel size wins so no tile is
    # downsampled. Y resolution is constant across GLO-30 (~1/3600 deg);
    # X resolution widens with latitude, so take the min (finest) in degrees.
    px_w = min(abs((info.right - info.left) / info.width) for info in infos)
    px_h = min(abs((info.top - info.bottom) / info.height) for info in infos)

    out_left = min(info.left for info in infos)
    out_top = max(info.top for info in infos)
    out_right = max(info.right for info in infos)
    out_bottom = min(info.bottom for info in infos)

    out_width = max(1, round((out_right - out_left) / px_w))
    out_height = max(1, round((out_top - out_bottom) / px_h))

    crs_wkt = infos[0].crs.to_wkt()
    dtype = infos[0].dtype
    nodata = infos[0].nodata

    gdal_dtype = {
        "float32": "Float32",
        "float64": "Float64",
        "int16": "Int16",
        "int32": "Int32",
        "uint16": "UInt16",
        "uint8": "Byte",
    }.get(str(dtype), "Float32")

    sources_xml = []
    for info in infos:
        dst_x = round((info.left - out_left) / px_w)
        dst_y = round((out_top - info.top) / px_h)
        dst_w = round((info.right - info.left) / px_w)
        dst_h = round((info.top - info.bottom) / px_h)

        sources_xml.append(f"""
      <ComplexSource>
        <SourceFilename relativeToVRT="0">{escape(info.path)}</SourceFilename>
        <SourceBand>1</SourceBand>
        <SrcRect xOff="0" yOff="0" xSize="{info.width}" ySize="{info.height}"/>
        <DstRect xOff="{dst_x}" yOff="{dst_y}" xSize="{dst_w}" ySize="{dst_h}"/>
        {"<NODATA>" + str(nodata) + "</NODATA>" if nodata is not None else ""}
      </ComplexSource>""")

    vrt_xml = f"""<VRTDataset rasterXSize="{out_width}" rasterYSize="{out_height}">
  <SRS>{escape(crs_wkt)}</SRS>
  <GeoTransform>{out_left}, {px_w}, 0.0, {out_top}, 0.0, {-px_h}</GeoTransform>
  <VRTRasterBand dataType="{gdal_dtype}" band="1">
    {"<NoDataValue>" + str(nodata) + "</NoDataValue>" if nodata is not None else ""}
    {"".join(sources_xml)}
  </VRTRasterBand>
</VRTDataset>
"""

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(vrt_xml)
    print(f"Wrote VRT mosaic: {out} ({out_width}x{out_height}px, {len(infos)} tiles)")
    return out