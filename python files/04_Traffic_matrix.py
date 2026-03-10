import pandas as pd
import numpy as np

print("Loading raw nodes and distance matrix...")
# Load your node coordinates and the clean distance matrix
nodes_df = pd.read_csv('csv files/dubai_delivery_nodes.csv', index_col='node_id')
distance_df = pd.read_csv('csv files/distance_matrix_local.csv', index_col=0)

# 1. Define the Sheikh Zayed Road (SZR) Bounding Box
# These coordinates roughly box in the SZR corridor passing between JLT and Marina
SZR_MIN_LAT, SZR_MAX_LAT = 25.065, 25.085
SZR_MIN_LON, SZR_MAX_LON = 55.135, 55.155

# 2. Function to check if a node falls inside this traffic heavy zone
def in_traffic_zone(lat, lon):
    return (SZR_MIN_LAT <= lat <= SZR_MAX_LAT) and (SZR_MIN_LON <= lon <= SZR_MAX_LON)

# 3. Map every node to a True/False value indicating if it's in the traffic zone
traffic_nodes = {
    node_id: in_traffic_zone(row['latitude'], row['longitude']) 
    for node_id, row in nodes_df.iterrows()
}

# 4. Apply the Traffic Multiplier
# We'll represent the 8 AM - 10 AM crawl by increasing the "cost" (distance) by 80%
TRAFFIC_MULTIPLIER = 1.8

dist_matrix = distance_df.values.astype(float)
node_ids = distance_df.index.tolist()

print(f"Applying a {TRAFFIC_MULTIPLIER}x penalty to routes intersecting SZR...")

# Iterate through the matrix. If a route starts or ends in the SZR zone, penalize it.
for i, origin_id in enumerate(node_ids):
    for j, dest_id in enumerate(node_ids):
        if i != j: # Ignore distance to itself
            if traffic_nodes[origin_id] or traffic_nodes[dest_id]:
                dist_matrix[i][j] *= TRAFFIC_MULTIPLIER

# 5. Convert back to integers (required by OR-Tools) and save
penalized_distance_df = pd.DataFrame(
    np.round(dist_matrix).astype(int), 
    index=node_ids, 
    columns=node_ids
)

penalized_distance_df.to_csv('csv files/distance_matrix_penalized.csv')
print("Success! Traffic-weighted matrix saved as 'distance_matrix_penalized.csv'")