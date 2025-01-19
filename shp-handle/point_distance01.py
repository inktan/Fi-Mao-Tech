import geopandas as gpd
import random
from geopy.distance import geodesic

def load_shapefile(file_path):
    """Load a shapefile containing points and return a GeoDataFrame."""
    gdf = gpd.read_file(file_path)
    # Ensure the geometry column contains Point objects
    if not gdf.geom_type[0] == 'Point':
        raise ValueError("The shapefile does not contain point geometry.")
    return gdf

def get_random_points(gdf, num_points=2):
    """Get a specified number of random points from a GeoDataFrame."""
    random_indices = random.sample(range(len(gdf)), num_points)
    print(random_indices)
    random_points_gdf = gdf.iloc[random_indices]
    random_points_gdf = gdf.iloc[[1,2]]
    return random_points_gdf

def main(shapefile_path):
    # Load the shapefile
    gdf = load_shapefile(shapefile_path)
    
    # Get two random points
    random_points = get_random_points(gdf, num_points=2)

    point1 = random_points.iloc[0]['geometry']
    point2 = random_points.iloc[1]['geometry']

    print(point1.distance(point2))

    coords1 = (point1.y, point1.x)  # Note: geopy expects (latitude, longitude)
    coords2 = (point2.y, point2.x)

    distance = geodesic(coords1, coords2).meters
    # return distance
    print(distance)
    
    # Print the coordinates of the random points
    # for idx, row in random_points.iterrows():
    #     print(f"Point {idx + 1}: {row['geometry'].x}, {row['geometry'].y}")

if __name__ == "__main__":
    shapefile_path = r'e:\work\sv_nadingzichidefangtoushi\merged_coordinates_01.shp'  # Replace with your shapefile path
    main(shapefile_path)