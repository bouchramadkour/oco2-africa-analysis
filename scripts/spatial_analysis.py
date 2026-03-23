#For functions related to gridding, clipping to Africa, and GeoPandas operations

import geopandas as gpd
from shapely.geometry import Point, box

def filter_by_africa_bounds(df):
    """Filters data within a rough bounding box of Africa."""
    return df[
        (df["latitude"].between(-40, 40)) & 
        (df["longitude"].between(-20, 60))
    ].copy()

def create_geodataframe_from_grid(df):
    """Groups data into a 1-degree grid using Points."""
    df['lat_grid'] = df['latitude'].round()
    df['lon_grid'] = df['longitude'].round()
    grid = df.groupby(['lat_grid', 'lon_grid', 'month'])['xco2'].mean().reset_index()
    grid['geometry'] = grid.apply(lambda r: Point(r['lon_grid'], r['lat_grid']), axis=1)
    return gpd.GeoDataFrame(grid, geometry='geometry', crs="EPSG:4326")

def create_geodataframe_polygons(df):
    """Creates a GeoDataFrame where each grid cell is a 1x1 degree square."""
    df['lat_grid'] = df['latitude'].round()
    df['lon_grid'] = df['longitude'].round()
    grid = df.groupby(['lat_grid', 'lon_grid'])['xco2'].mean().reset_index()
    
    # Create the square boxes
    grid["geometry"] = grid.apply(
        lambda row: box(
            row["lon_grid"] - 0.5, row["lat_grid"] - 0.5,
            row["lon_grid"] + 0.5, row["lat_grid"] + 0.5
        ), axis=1
    )
    return gpd.GeoDataFrame(grid, geometry="geometry", crs="EPSG:4326")

def get_africa_shape(shp_path):
    """Loads and returns the African continent boundary."""
    world = gpd.read_file(shp_path)
    return world[world["CONTINENT"] == "Africa"]

def clip_to_africa(gdf_grid, africa_shape):
    """Clips the gridded points to the exact shape of Africa."""
    return gpd.clip(gdf_grid, africa_shape)

import rasterio

def extract_land_cover(df, tif_path):
    """Extracts the Land Cover value from a .tif file for each lat/lon point."""
    with rasterio.open(tif_path) as src:
        # We transform lat/lon into coordinates the tif understands
        coord_list = [(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        
        # Sample the raster at these coordinates
        # src.sample returns a generator, we take the first value [0] of each sample
        df['land_cover_code'] = [val[0] for val in src.sample(coord_list)]
        
    return df