# French Cities Hexagon Generator

This project generates hexagonal grids around the 20 largest cities in France. The hexagons are created with a side length of 57.7 meters and cover a 3km radius around each city center.

## Features

- Generates hexagons for 20 major French cities
- Converts coordinates between WGS84 (GPS) and Lambert-93 (French projection)
- Exports coordinates to CSV format
- Includes visualization capabilities

## Requirements

- Python 3.x
- Required packages (see requirements.txt):
  - geopandas
  - shapely
  - numpy
  - pandas
  - pyproj
  - tqdm

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python script.py
```

This will generate a CSV file containing the coordinates of all hexagons.

## Output

The script generates a CSV file (`hexagones_20_villes_france_coordinates.csv`) containing:
- Center points of each hexagon
- Vertices of each hexagon
- City name and hexagon group number

## License

[Your chosen license] 