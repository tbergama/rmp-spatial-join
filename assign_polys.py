#!/usr/bin/env python

import argparse
import os
import pandas as pd
import geopandas as gpd

if __name__ == '__main__':

    # ----- parse arguments ----------------------------------------------------

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--data",
        required=True,
        help="File path to data .csv"
    )

    parser.add_argument(
        "-p", "--polygons",
        help="File path to polygon .shp"
    )

    parser.add_argument(
        "-l", 
    )

    args = parser.parse_args()

    print(args.data)
    print(args.polygons)
