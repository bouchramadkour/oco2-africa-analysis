#For your plotting functions (maps and seasonal plots)

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.ticker as mticker
from shapely.geometry import Point
import geopandas as gpd

# Helper function to avoid repeating map settings
def _apply_map_style(ax, title):
    ax.set_title(title)
    ax.set_extent([-20, 60, -40, 40], crs=ccrs.PlateCarree())

def plot_annual_mean_map(gdf_clipped, africa_shape):
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    """Plots the single annual mean map using the box polygons."""
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": ccrs.PlateCarree()})
    
    # Plot the data
    gdf_clipped.plot(
        ax=ax, column="xco2", cmap="viridis",
        vmin=420, vmax=424, legend=True,
        legend_kwds={'label': "Mean XCO2 (ppm)", 'orientation': "vertical", 'shrink': 0.7}
    )
    africa_shape.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
    
    _apply_map_style(ax, "Mean XCO2 over Africa (Annual)")

    # # ✅ Add gridlines first
    # gl = ax.gridlines(
    #     draw_labels=True, 
    #     linewidth=0.5, color='gray', alpha=0.5, linestyle='--'
    # )
    # gl.top_labels = False
    # gl.right_labels = False

    # # ✅ Format longitude and latitude
    # gl.xformatter = LONGITUDE_FORMATTER
    # gl.yformatter = LATITUDE_FORMATTER

    # # ✅ Set spacing
    # gl.xlocator = mticker.FixedLocator([-20, 0, 20, 40, 60])
    # gl.ylocator = mticker.FixedLocator([-40, -20, 0, 20, 40])

    # # Optional: control label font size
    # gl.xlabel_style = {'size': 10}
    # gl.ylabel_style = {'size': 10}
    # latitude / longitude (optionnel mais propre)
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False

    plt.savefig("./results/annual_co2_map.png", dpi=300, bbox_inches='tight')
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
    plt.savefig("./results/seasonal_co2_map.png", dpi=300, bbox_inches='tight')
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
    plt.savefig("./results/monthly_co2_map.png", dpi=300, bbox_inches='tight')
    plt.show()

#for land cover plotting
def plot_land_cover(lc_data, extent, cmap, palette, labels):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import matplotlib.ticker as mticker
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

    plt.figure(figsize=(12, 10))

    plt.imshow(
        lc_data,
        cmap=cmap,
        vmin=0,
        vmax=17,
        extent=extent,
        origin='upper'
    )

    plt.title("MODIS Land Cover Africa 2024", fontsize=16)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Gridlines
    ax = plt.gca()
    plt.gca().set_xticks([-20, -10, 0, 10, 20, 30, 40, 50, 60])
    plt.gca().set_yticks([-40, -30, -20, -10, 0, 10, 20, 30, 40])
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    plt.grid(True, linestyle='--', alpha=0.5)

    # Legend
    patches = [Patch(color=palette[i], label=labels[i]) for i in range(len(labels))]
    plt.legend(
        handles=patches,
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        fontsize=9,
        title="Land Cover Types"
    )

    plt.tight_layout()
    plt.savefig("./results/land_cover_africa.png", dpi=300, bbox_inches='tight')
    plt.show()


