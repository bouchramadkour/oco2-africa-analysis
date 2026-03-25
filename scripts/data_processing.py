#For functions that handle NetCDF to CSV conversion and filtering

import os
import xarray as xr
import pandas as pd

def extract_date_from_filename(filename):
    """Extracts year, month, day from OCO2 filename format."""
    date_part = filename.split("_")[2]
    return {
        "year": int("20" + date_part[:2]),
        "month": int(date_part[2:4]),
        "day": int(date_part[4:6])
    }

def process_single_nc4(file_path, date_info):
    """Opens one NetCDF, filters it, and returns a DataFrame."""
    # engine="netcdf4" and decode_times=False prevents HDF/Runtime errors
    with xr.open_dataset(file_path, engine="netcdf4", decode_times=False) as ds:
        df = pd.DataFrame({
            "sounding_id": ds['sounding_id'].values,
            "xco2": ds['xco2'].values,
            "xco2_quality_flag": ds['xco2_quality_flag'].values,
            "latitude": ds['latitude'].values,
            "longitude": ds['longitude'].values,
            **date_info # Unpacks year, month, day
        })
    return df[df['xco2_quality_flag'] == 0].dropna()

def convert_all_nc4_to_csv(input_dir, output_dir):
    """Orchestrates the conversion of all files in a folder."""
    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(input_dir) if f.endswith(".nc4")]
    
    for f in files:
        date_info = extract_date_from_filename(f)
        df = process_single_nc4(os.path.join(input_dir, f), date_info) # /data/file1.nc4
        
        output_name = f.replace(".nc4", ".csv") # file1.nc4 -> file1.csv
        df.to_csv(os.path.join(output_dir, output_name), index=False) # /data_csv/file1.csv #index=False prevents writing row numbers to the CSV (index column : 0, 1, 2, etc.) which is not needed here since we have a unique sounding_id for each row.
    print(f"Processed {len(files)} files.")

def load_combined_dataframe(csv_dir):
    """Combines all CSVs into one single DataFrame."""
    files = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith(".csv")]
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

def get_season(month):
    """Categorizes month into DJF, MAM, JJA, or SON."""
    if month in [12, 1, 2]: return "DJF"
    if month in [3, 4, 5]: return "MAM"
    if month in [6, 7, 8]: return "JJA"
    return "SON"