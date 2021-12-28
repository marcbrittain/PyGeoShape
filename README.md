# PyGeoShape
3D extension to [shapely](https://github.com/shapely/shapely/tree/main) and [pyproj](https://github.com/pyproj4/pyproj) to make working with geospatial/trajectory data easier in python.

## Getting Started
### Installation

#### pip
The easiest way to install PyGeoShape is by using pip:

```bash
pip install pygeoshape
```

#### source

To install the package from source, first clone the repository to a location of your choosing:

```bash
git clone https://github.com/marcbrittain/PyGeoShape.git

```

Then navigate to the directory:

```bash
cd PyGeoShape
```

Then install using pip (note: requires python 3.6+):

```bash
pip install -e .
```

### Examples
The core focus of this repository is to make working with 3D geospatial/geographical data easier in python. Therefore, the core element of this repository is the GeoLineString (to start).

1. [GeoLineStrings](https://github.com/marcbrittain/PyGeoShape/blob/main/Examples/Example%20-%20GeoLineStrings.ipynb)

## Roadmap

This project is very early on and is something that I am working on in my free time. Getting some of the initial functionality of GeoLineStrings like intersections and coordinate transformations was a first step, but there is a long way to go. Here I list some of the next major items that need to be addressed.

* GeoLineStrings
  1. Handling heterogeneous intersection types (LineString, Point, etc.)
  2. Add function for distance calculation
  3. Add function for GeoLineString splits
  4. Optimize intersection function for efficiency


* GeoPoint
  1. Port GeoLineString functionality to GeoPoint


* Add additional Geo Types
  1. GeoMultiLineString
  2. GeoMultiPoint



## Contributing

Contributions are always welcome. Please follow standard PEP-8 code format for contributions.
