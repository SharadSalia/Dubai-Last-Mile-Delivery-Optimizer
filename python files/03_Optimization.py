import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

print("Loading distance matrix...")
# Load the 2D matrix generated in Task 2.2
distance_df = pd.read_csv('csv files/distance_matrix_penalized.csv', index_col=0)

# OR-Tools requires the matrix to be a standard Python list of lists
distance_matrix = distance_df.values.tolist()
num_locations = len(distance_matrix)

# 1. Create the Data Model
def create_data_model():
    """Stores the data for the routing problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = 15 # Simulating a fleet of 15 delivery vans
    data['depot'] = 0 # Assume the first node in our list is the Aramex/Noon depot
    
    # Simulate delivery demands: each location needs 1 to 3 packages 
    # (Depot has 0 demand)
    np.random.seed(42)
    demands = np.random.randint(1, 4, size=num_locations)
    demands[0] = 0 
    data['demands'] = demands.tolist()
    
    # Vehicle capacities: each van can hold 100 packages
    data['vehicle_capacities'] = [100] * data['num_vehicles']
    return data

data = create_data_model()

# 2. Initialize the Routing Manager and Model
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                       data['num_vehicles'], data['depot'])
routing = pywrapcp.RoutingModel(manager)

# 3. Create the Distance Callback
def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# 4. Add the "Driver Shift Hours" Constraint (represented here as max distance)
# Let's cap each driver at 30,000 meters (30 km) for their Dubai Marina shift
dimension_name = 'Distance'
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    30000,  # vehicle maximum travel distance in meters
    True,  # start cumul to zero
    dimension_name)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)

# 5. Add the "Vehicle Capacity" Constraint
def demand_callback(from_index):
    """Returns the demand of the node."""
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # null capacity slack
    data['vehicle_capacities'],  # vehicle maximum capacities
    True,  # start cumul to zero
    'Capacity')

# 6. Set Search Parameters and Solve
print("Running optimization engine... This may take a few seconds.")
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.FromSeconds(10) # Let it search for 10 seconds to find a great route

solution = routing.SolveWithParameters(search_parameters)

if solution:
    print("Optimization successful! Found efficient routes.")
    # You can print out the exact routes here, or save them to map in Phase C
else:
    print("No solution found. We might need more vehicles or higher capacities.")