import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import haversine_distances

print("Loading delivery nodes...")
# Load the CSV you generated in Task 2.1
df = pd.read_csv('csv files/dubai_delivery_nodes.csv')

# The haversine_distances function requires coordinates in radians, 
# and strictly in the order of [latitude, longitude]
points_in_radians = np.radians(df[['latitude', 'longitude']].values)

print("Calculating 250,000 distance pairs natively...")
# Calculate the pairwise distance matrix (result is in radians)
dist_matrix_radians = haversine_distances(points_in_radians, points_in_radians)

# Multiply by Earth's radius in meters (approx 6,371,000 meters) to get real-world distance
dist_matrix_meters = dist_matrix_radians * 6371000

# Convert the resulting 2D NumPy array back into a readable Pandas DataFrame.
# We use the node_ids as both the rows (index) and the columns.
distance_matrix_df = pd.DataFrame(
    dist_matrix_meters, 
    index=df['node_id'], 
    columns=df['node_id']
)

# Convert float distances to integers. 
# The OR-Tools optimization engine we use in the next step requires integer values!
distance_matrix_df = distance_matrix_df.astype(int)

# Save to a local CSV
distance_matrix_df.to_csv('csv files/distance_matrix_local.csv')
print("Success! Matrix saved as 'distance_matrix_local.csv'")