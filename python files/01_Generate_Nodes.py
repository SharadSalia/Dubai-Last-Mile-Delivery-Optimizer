import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Define the specific neighborhoods in Dubai
places = [
    "Dubai Marina, Dubai, United Arab Emirates", 
    "Jumeirah Lake Towers, Dubai, United Arab Emirates"
]

print("Fetching street network from OpenStreetMap. This might take a minute...")

# 2. Download the 'drive' network graph for these areas
# retain_all=False ensures we only get connected roads (ignoring isolated segments)
G = ox.graph_from_place(places, network_type='drive', simplify=True, retain_all=False)

# 3. Convert the graph into GeoDataFrames for Nodes (intersections/points) and Edges (roads)
nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

print(f"Total navigable nodes found: {len(nodes_gdf)}")

# 4. Sample 500 random delivery points from the available nodes
# random_state ensures reproducibility if you need to re-run the exact same points
delivery_points = nodes_gdf.sample(n=500, random_state=42, replace=True)

# 5. Extract just the necessary columns (Node ID, Longitude, Latitude) for your SQL matrix later
delivery_export = delivery_points[['x', 'y']].rename(columns={'x': 'longitude', 'y': 'latitude'})
delivery_export.index.name = 'node_id'

# Save to CSV so you can upload it to BigQuery for Task 2.2
delivery_export.to_csv('dubai_delivery_nodes.csv')
print("Saved 500 delivery points to 'dubai_delivery_nodes.csv'")

# 6. Quick Visualization (Sanity Check)
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the road network in light gray
edges_gdf.plot(ax=ax, linewidth=0.5, color='lightgray')

# Plot our 500 delivery points in red
delivery_points.plot(ax=ax, color='red', markersize=10, alpha=0.7)

plt.title("500 Simulated Delivery Points in Dubai Marina & JLT", fontsize=15)
plt.axis('off') # Hide axes for a cleaner map
plt.show()