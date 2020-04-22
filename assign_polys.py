#!/usr/bin/env python

import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd
import warnings

if __name__ == '__main__':

    # ----- Parse Arguments -----

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--data",
        required=True,
        help="File path to data .csv (use \"/\" not \"\\\")"
    )

    parser.add_argument(
        "-p", "--polygons",
        default=None,
        help="File path to polygon .shp (use \"/\" not \"\\\")"
    )

    parser.add_argument(
        "--lat",
        default="latitude",
        help="Name of latitude column in data csv (default is \"latitude\")"
    )

    parser.add_argument(
        "--lon",
        default="longitude",
        help="Name of longitude column in data csv (default is \"longitude\")"
    )

    parser.add_argument(
        "--nullvals",
        default=None,
        help="Comma seperated list of values to interpret as null when reading the data csv " \
             "(ex: --nullvals \"list,of,vals\")"
    )

    args = parser.parse_args()

    # ----- Validate Arguments -----

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Handle default polygon path
    if args.polygons is None:
        try:
            from config import poly_path
            poly_path = Path(poly_path)
        except:
            print("Polygon path was not provided and no default was found.")
            print("Provide a polygon path with -p/--polygons or set default path by running: " \
                  "echo poly_path=\"path/to/polys.shp\" > config.py")
            print("Exiting...")
            exit(1)
    else:
        poly_path = Path(args.polygons)

    # Check that files exist
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Data path does not exist: {data_path}")
        print("Please provide a valid data path with the -d/--data argument.")
        print("Exiting...")
        exit(1)

    if not poly_path.exists():
        print(f"Polygons path does not exist: {poly_path}")
        print("Please provide a valid polygons path with the -p/--polygons argument or set default path by running:" \
              "echo poly_path=\"path/to/polys.shp\" > config.py")
        print("Exiting...")
        exit(1)

    # Try to read data from files
    try:
        print(f"Reading {data_path}")
        if args.nullvals is not None:
            null_vals = args.nullvals.split(",")
        else:
            null_vals = None
        df_data = pd.read_csv(data_path, na_values=null_vals)
        print("Success.")
    except:
        print("Error reading data file. Exiting...")
        exit(1)

    try:
        print(f"Reading {poly_path}")
        gdf_poly = gpd.read_file(poly_path)
        print("Success.")
    except:
        print("Error reading polygon file. Exiting...")
        exit(1)

    # Confirm that provided latitude/longitude column names exist in df_data
    lat_col = args.lat
    lon_col = args.lon

    if lat_col not in df_data.columns.values:
        print(f"{lat_col} is not a valid column in provided dataset")
        print("Please verify the correct column name and try again")
        print("Exiting...")
        exit(1)

    if lon_col not in df_data.columns.values:
        print(f"{lon_col} is not a valid column in provided dataset")
        print("Please verify the correct column name and try again")
        print("Exiting...")
        exit(1)

    # ----- Perform Spatial Join ------

    # Convert dataframe to geodataframe
    print("Creating points from data lat/lon columns...")

    try:
        df_data.astype({lat_col: 'float64',
                        lon_col: 'float64'})
        gdf_data = gpd.GeoDataFrame(df_data, geometry=gpd.points_from_xy(df_data[lon_col], df_data[lat_col]))
        print("Success.")
    except:
        print("Couldn't make points from provided lat/lon data")
        print("Exiting...")
        exit(1)

    # Perform spatial join
    print("Performing spatial join...")
    try:
        gdf_joined = gpd.sjoin(gdf_data, gdf_poly, op='within', how='left')
        print("Success.")
    except:
        print("Spatial join failed.")
        print("Exiting...")
        exit(1)

    # ----- Write result to CSV -----

    # Convert joined geodataframe to pandas dataframe
    df_joined = pd.DataFrame(gdf_joined.drop(columns="geometry"))

    # Append "SpatialJoin" to the data file name
    fname = data_path.name.split(".")[0]+"SpatialJoin.csv"

    # Write csv
    print("Writing CSV...")
    try:
        df_joined.to_csv(fname)
        print("Success.")
    except:
        print("Could not write result.")
        print("Exiting...")
        exit(1)

