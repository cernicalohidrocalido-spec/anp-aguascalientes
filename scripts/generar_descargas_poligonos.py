import json, os, zipfile, io
import shapefile

GEOJSON_PATH = r"C:\SIG\APC2024\final\sitio_anp\data\anp_poligonos.geojson"
OUT_DIR = r"C:\SIG\APC2024\final\sitio_anp\assets\descargas"

os.makedirs(OUT_DIR, exist_ok=True)

WGS84_PRJ = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
             'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')

def ring_to_kml_coords(ring):
    return " ".join(f"{lon},{lat},0" for lon, lat in ring)

def polygon_kml_geometry(coords):
    # coords: list of rings (outer + holes), first is outer
    outer = coords[0]
    boundary = f'<outerBoundaryIs><LinearRing><coordinates>{ring_to_kml_coords(outer)}</coordinates></LinearRing></outerBoundaryIs>'
    holes = ""
    for hole in coords[1:]:
        holes += f'<innerBoundaryIs><LinearRing><coordinates>{ring_to_kml_coords(hole)}</coordinates></LinearRing></innerBoundaryIs>'
    return f'<Polygon><tessellate>1</tessellate>{boundary}{holes}</Polygon>'

def geometry_to_kml(geom):
    if geom["type"] == "Polygon":
        return polygon_kml_geometry(geom["coordinates"])
    elif geom["type"] == "MultiPolygon":
        parts = "".join(polygon_kml_geometry(poly) for poly in geom["coordinates"])
        return f'<MultiGeometry>{parts}</MultiGeometry>'
    raise ValueError("unsupported geometry type: " + geom["type"])

def write_shp_zip(feat, out_path):
    props = feat["properties"]
    geom = feat["geometry"]
    buf_shp, buf_shx, buf_dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()
    w = shapefile.Writer(shp=buf_shp, shx=buf_shx, dbf=buf_dbf, shapeType=shapefile.POLYGON)
    w.field("id", "C", 40)
    w.field("nombre", "C", 100)
    w.field("municipios", "C", 254)
    w.field("hectareas", "N", 19, 4)

    if geom["type"] == "Polygon":
        parts = geom["coordinates"]
    else:  # MultiPolygon -> flatten all polygon rings into one shp record's parts
        parts = []
        for poly in geom["coordinates"]:
            parts.extend(poly)

    # shapefile polygons require clockwise outer rings; ensure via shapefile writer's own handling
    w.poly(parts)
    w.record(
        str(props.get("id", ""))[:40],
        str(props.get("nombre", ""))[:100],
        str(props.get("municipios", ""))[:254],
        float(props.get("hectareas") or 0),
    )
    w.close()

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        base = props["id"]
        zf.writestr(f"{base}.shp", buf_shp.getvalue())
        zf.writestr(f"{base}.shx", buf_shx.getvalue())
        zf.writestr(f"{base}.dbf", buf_dbf.getvalue())
        zf.writestr(f"{base}.prj", WGS84_PRJ)
        zf.writestr(f"{base}.cpg", "UTF-8")

def write_kmz(feat, out_path):
    props = feat["properties"]
    geom = feat["geometry"]
    nombre = props.get("nombre", props.get("id", ""))
    kml_geom = geometry_to_kml(geom)
    kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>{nombre}</name>
<Placemark>
<name>{nombre}</name>
<description>Municipios: {props.get("municipios","")} | Superficie: {props.get("hectareas","")} ha</description>
<Style><LineStyle><color>ff2d6a4f</color><width>2</width></LineStyle><PolyStyle><color>6652b788</color></PolyStyle></Style>
{kml_geom}
</Placemark>
</Document>
</kml>'''
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml.encode("utf-8"))

gj = json.load(open(GEOJSON_PATH, encoding="utf-8"))
count = 0
for feat in gj["features"]:
    fid = feat["properties"]["id"]
    write_shp_zip(feat, os.path.join(OUT_DIR, f"{fid}_shp.zip"))
    write_kmz(feat, os.path.join(OUT_DIR, f"{fid}.kmz"))
    count += 1

print(f"generated {count} SHP zips and {count} KMZ files in {OUT_DIR}")
