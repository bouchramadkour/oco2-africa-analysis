#For your plotting functions (maps and seasonal plots)

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib as mpl
from shapely.geometry import Point
import geopandas as gpd

# Helper function to avoid repeating map settings
def _apply_map_style(ax, title):
    ax.set_title(title)
    ax.set_extent([-20, 60, -40, 40], crs=ccrs.PlateCarree())

def plot_annual_mean_map(gdf_clipped, africa_shape):
    """Plots the single annual mean map using the box polygons."""
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": ccrs.PlateCarree()})
    
    gdf_clipped.plot(
        ax=ax, column="xco2", cmap="viridis",
        vmin=420, vmax=424, legend=True,
        legend_kwds={'label': "Mean XCO2 (ppm)", 'orientation': "vertical", 'shrink': 0.7}
    )
    africa_shape.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
    _apply_map_style(ax, "Mean XCO2 over Africa (Annual)")
    plt.show()

def plot_seasonal_maps(df_africa, africa_shape):
    """Plots the 2x2 seasonal grid."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()
    seasons = ["DJF", "MAM", "JJA", "SON"]

    for i, season in enumerate(seasons):
        ax = axes[i]
        df_s = df_africa[df_africa["season"] == season]
        
        # Grid it internally for the specific season
        grid_s = df_s.groupby(['lat_grid','lon_grid'])['xco2'].mean().reset_index()
        grid_s['geometry'] = grid_s.apply(lambda r: Point(r['lon_grid'], r['lat_grid']), axis=1)
        gdf_s = gpd.GeoDataFrame(grid_s, geometry='geometry', crs="EPSG:4326")
        gdf_clipped = gpd.clip(gdf_s, africa_shape)

        gdf_clipped.plot(ax=ax, column='xco2', cmap='viridis', marker='s', markersize=150, vmin=420, vmax=424)
        africa_shape.boundary.plot(ax=ax, edgecolor='black', linewidth=1)
        _apply_map_style(ax, season)
        ax.set_xticks([]); ax.set_yticks([])

    # Add shared colorbar
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=mpl.colors.Normalize(vmin=420, vmax=424))
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(sm, cax=cbar_ax, label='Mean XCO2 (ppm)')
    plt.show()

def plot_monthly_timeseries(df_africa):
    """Plots the simple line chart of CO2 by month."""
    monthly_co2 = df_africa.groupby('month')['xco2'].mean()
    
    plt.figure(figsize=(10, 5))
    monthly_co2.plot(marker='o', color='forestgreen')
    plt.xlabel("Month")
    plt.ylabel("Mean XCO2 (ppm)")
    plt.title("Mean XCO2 in Africa by Month")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

def plot_monthly_grid(gdf_final_points, africa_shape):
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    fig, axes = plt.subplots(4, 3, figsize=(18, 16), subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()
    for m in range(1, 13):
        ax = axes[m-1]
        gdf_m = gdf_final_points[gdf_final_points['month'] == m]
        if not gdf_m.empty:
            gdf_m.plot(ax=ax, column='xco2', cmap='viridis', marker='s', markersize=60, vmin=420, vmax=424)
        africa_shape.boundary.plot(ax=ax, edgecolor='black', linewidth=1)
        _apply_map_style(ax, month_names[m-1])
    plt.show()

import seaborn as sns

def plot_co2_by_land_cover(df):
    """Draws a boxplot showing CO2 distribution for each land cover type."""
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='land_cover_name', y='xco2', data=df)
    plt.xticks(rotation=45)
    plt.title("XCO2 Distribution by Land Cover Type in Africa")
    plt.ylabel("XCO2 (ppm)")
    plt.show()