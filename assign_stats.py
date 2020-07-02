#!/usr/bin/env python

import pandas as pd
import numpy as np
from pathlib import Path
import os 
import string
import argparse
from pathlib import Path
import warnings
import logging
os.getcwd()

if __name__ == '__main__':

    # ----- Set Up Logging ------

    logfile = "assign_stats.log"

    # Delete any old logfile
    if os.path.exists(logfile):
        os.remove(logfile)

    # Initialize logfile
    FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
    logging.basicConfig(filename=logfile, format=FORMAT)

    # ----- Parse Arguments -----

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--data",
        required=True,
        help="File path to data .csv"
    )

    parser.add_argument(
        "-p", "--parameters",
        default=None,
        help="File path to constituents .txt"
    )

    parser.add_argument(
        "--nullvals",
        default=None,
        help="Comma seperated list of values to interpret as null when reading the data csv " \
             "(ex: --nullvals \"list,of,vals\")"
    )

    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Directory to output files to"
    )

    args = parser.parse_args()

    # ----- Validate Arguments -----

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Handle default polygon path
    if args.stats is None:
        try:
            from config import parameters_path
            parameters_path = Path(parameters_path)
        except:
            logging.exception("Parameters path was not provided and no default was found.")
            print("Parameters path was not provided and no default was found.")
            print("Provide a data path with -p/--parameters or set default path by running: " \
                  "echo parameters_path=\"path/to/parameters.txt\" > config.py")
            print("Exiting...")
            exit(1)
    else:
        parameters_path = Path(args.stats)

    if not parameters_path.exists():
        print(f"Parameters path does not exist: {parameters_path}")
        print("Please provide a valid parameters path with the -p/--parameters argument or set default path by running:" \
              "echo parameters_path=\"path/to/parameters.txt\" > config.py")
        print("Exiting...")
        exit(1)

    # Check that files exist
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Data path does not exist: {data_path}")
        print("Please provide a valid data path with the -d/--data argument.")
        print("Exiting...")
        exit(1)

    try:
        print(f"Reading {poly_path}")
        gdf_poly = gpd.read_file(poly_path)
        print("Success.")
    except:
        logging.exception("Error reading polygon file.")
        print("Error reading polygon file. Exiting...")
        exit(1)

    lat_col = args.lat
    lon_col = args.lon

    output_path = Path(args.output)

    # Create output directory if it doesn't exist
    if not output_path.exists():
        os.mkdir(output_path)

    # If a directory was passed for data path, build list of files in directory
    data_files = []
    if os.path.isdir(data_path):
        data_files.extend([Path(os.path.join(data_path, f)) for f in os.listdir(data_path) if
                           os.path.isfile(os.path.join(data_path, f))])
    else:
        data_files = [data_path]

    # For each data file...
    for f in data_files:
        # Try to read data from file
        try:
            print(f"Reading {f}")

            # Handle Nulls
            if args.nullvals is not None:
                null_vals = args.nullvals.split(",")
            else:
                null_vals = None

            # Handle filetype
            extension = f.name.split(".")[1]
            if extension == "csv":
                df_data = pd.read_csv(f, na_values=null_vals)
            if extension == "xlsx":
                df_data = pd.read_excel(f, na_values=null_vals)
            else:
                print("Error reading data file.")
                print(f"{f} has an unsupported file extension.")
                print("Exiting...")
                exit(1)

            print("Success.")
        except:
            logging.exception("Error reading data file.")
            print("Error reading data file. Exiting...")
            exit(1)

        # Confirm that provided latitude/longitude column names exist in df_data
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
            logging.exception("Couldn't make points from provided lat/lon data")
            print("Couldn't make points from provided lat/lon data")
            print("Exiting...")
            exit(1)

        # Perform spatial join
        print("Performing spatial join...")
        try:
            gdf_joined = gpd.sjoin(gdf_data, gdf_poly, op='within', how='left')
            print("Success.")
        except:
            logging.exception("Spatial join failed.")
            print("Spatial join failed.")
            print("Exiting...")
            exit(1)

        # ----- Write result to CSV -----

        # Convert joined geodataframe to pandas dataframe
        df_joined = pd.DataFrame(gdf_joined.drop(columns="geometry"))

        # Append "_spatialJoin" to the data file name
        fname = f.name.split(".")[0]+"_spatialJoin.csv"

        # Write csv
        print("Writing CSV...")
        try:
            df_joined.to_csv(Path(output_path, fname), index=False)
            print("Success.")
        except:
            logging.exception("Could not write result.")
            print("Could not write result.")
            print("Exiting...")
            exit(1)

