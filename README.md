# rmp-spatial-join

A python utility to join point data with polygon shapefiles.

## Getting Started

To use the utility, you will need to set up a couple things first:

1. Clone this repository

`git clone https://github.com/tbergama/rmp-spatial-join.git`

2. [Install conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html) if you haven't already. You can opt for miniconda or the full anaconda install.

3. Set up conda environment
```
conda env create -f environment.yaml
conda activate rmp-spatial-join
```

## Using the Utility

The utility used by running `python assign_polys.py` with the appropriate arguments. If the utility is run successfully, a CSV will be produced in the `rmp-spatial-join` directory with "SpatialJoin" appended to the original data file name.

### Argument Descriptions

Get a description of the available arguments by running `python assign_polys.py --help`. For example:

```
(rmp-spatial-join) rmp-spatial-join>python assign_polys.py --help
usage: assign_polys.py [-h] -d DATA [-p POLYGONS] [--lat LAT] [--lon LON]
                       [--nullvals NULLVALS]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  File path to data .csv (use "/" not "\")
  -p POLYGONS, --polygons POLYGONS
                        File path to polygon .shp (use "/" not "\")
  --lat LAT             Name of latitude column in data csv (default is
                        "latitude")
  --lon LON             Name of longitude column in data csv (default is
                        "longitude")
  --nullvals NULLVALS   Comma seperated list of values to interpret as null
                        when reading the data csv (ex: --nullvals
                        "list,of,vals")
```

### Example Run

This is an example of a successful run of the utility. In this case, the data file is located at `C:\path\to\data.csv`, the polygon shapefile is located at `C:\path\to\polygons.shp`, the latitude and longitude column names in the data file are `Latitude` and `Longitude` respectively, and the data file uses `<Null>` to indicate null values.

```
(rmp-spatial-join) rmp-spatial-join>python assign_polys.py -d "C:\path\to\data.csv" -p "C:\path\to\polygons.shp" --lat Latitude --lon Longitude --nullvals "<Null>"
Reading C:\path\to\data.csv
Success.
Reading C:\path\to\polygons.shp
Success.
Creating points from data lat/lon columns...
Success.
Performing spatial join...
Success.
Writing CSV...
Success.
```

After the utility is run, you will find `dataSpatialJoin.csv` in the `rmp-spatial-join` directory. This file will contain everything that the original data file did, but a new colomn will be present with the IDs of the polygons they were assigned to.

### Setting Default Shapefile

If you will be running the utilty multiple times with the same shapefile and don't want to include it as an argument on every run, you can set a default shapefile path by running the following:

```
echo poly_path="C:\path\to\polygons.shp" > config.py
```
This should produce a file called `config.py` in the directory. To change the default path, delete this file and rerun the above line, or edit the variable inside the file.

### If you get Errors

If the utility fails for any reason, you will either see a message print the screen followed by `Exiting...`. If this happens, information about the error will be written to a file called  `assign_polys.log`. You can open up that file and try to determine what went wrong yourself, or if you can't figure it out you can create a new github issue with the contents of the logfile copy/pasted in, along with any other information you think might be useful to debug the issue and I will take a look.

Note that the logfile is generated everytime the utility is run, but will be empty if the run was successful. Also note that the logfile is deleted and rewritten on every run.

