# utils_map.py
import pandas as pd
import geopandas as gpd
import json
import numpy as np
import plotly.express as px
from pathlib import Path

# Variables disponibles
VARS_MEAN = [
    'Cloud_Cover_Mean_24h', 'elevation', 'relative_humidity',
    'surface_net_solar_radiation_sum', 'surface_pressure',
    'temperature_2m_C', 'total_precipitation_sum',
    'wind_direction', 'wind_speed', "radiation_pred"
]

def load_data(project_root: Path):
    """Carga CSV y GeoJSON desde la carpeta Datasets."""
    data_path = project_root / "Datasets"
    csv_path = data_path / "solar_with_predictions.csv"
    geojson_path = data_path / "Panama_Boundaries.geojson"

    df = pd.read_csv(csv_path)
    panama_map_data = json.load(open(geojson_path, encoding="utf-8"))
    gdf_bound = gpd.read_file(geojson_path, encoding="utf-8")

    return df, panama_map_data, gdf_bound


def process_data(df, gdf_bound):
    """Procesa datos y devuelve GeoDataFrame listo para graficar."""
    gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs="EPSG:4326")
    joined = gpd.sjoin(gdf_points, gdf_bound, how="left", predicate="within")

    base = gdf_bound[["ID_CORR", "Provincia", 'Corregimiento']].copy()
    base["ID_CORR"] = base["ID_CORR"].astype(str)
    joined["ID_CORR"] = joined["ID_CORR"].astype(str)

    corr_stats = (
        joined.groupby("ID_CORR")
        .agg({c: "mean" for c in VARS_MEAN})
        .reset_index()
    )

    full = base.merge(corr_stats, on="ID_CORR", how="left")

    prov_means = (
        full.groupby("Provincia")[VARS_MEAN]
        .mean()
        .add_prefix("prov_")
        .reset_index()
    )

    full = full.merge(prov_means, on="Provincia", how="left")

    for c in VARS_MEAN:
        global_mean = full[c].mean()
        if np.isnan(global_mean):
            global_mean = 0
        full[c + "_filled"] = full[c].fillna(full["prov_" + c]).fillna(global_mean)

    filled_cols = [c + "_filled" for c in VARS_MEAN]
    to_merge = ["ID_CORR", "Provincia", "Corregimiento"] + filled_cols

    gdf_bound["ID_CORR"] = gdf_bound["ID_CORR"].astype(str)
    gdf_bound2 = gdf_bound.merge(full[to_merge], on="ID_CORR", how="left", suffixes=("", "_dup"))

    for col in ["Provincia", "Corregimiento"]:
        dup = col + "_dup"
        if dup in gdf_bound2.columns:
            gdf_bound2[col] = gdf_bound2[col].fillna(gdf_bound2[dup])
            gdf_bound2.drop(columns=[dup], inplace=True)

    return gdf_bound2


def generate_map(gdf_bound2, panama_map_data, df, variable: str):
    """Genera mapa interactivo para la variable seleccionada."""
    fig = px.choropleth_mapbox(
        gdf_bound2,
        geojson=panama_map_data,
        locations="ID_CORR",
        featureidkey="properties.ID_CORR",
        color=f"{variable}_filled",
        mapbox_style="open-street-map",
        zoom=6,
        center={"lat": df["lat"].mean(), "lon": df["lon"].mean()},
        opacity=0.75,
        height=700,
        color_continuous_scale=[(0.0, "#88FF00"), (0.3, "#FFA500"), (1.0, "#FF0000")],
        hover_name="Corregimiento",
        hover_data={
            "ID_CORR": False, "Provincia": True, f"{variable}_filled": ":.2f"
        }
    )
    fig.update_layout(margin=dict(r=0, t=0, l=0, b=0))
    return fig