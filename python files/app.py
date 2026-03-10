import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import requests
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# --- APP CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Dubai Last-Mile Optimizer")
st.title("🚚 Dubai Last-Mile Delivery Optimizer")
st.markdown("Click on the map to add delivery stops. The engine will instantly calculate the most efficient route and your cost savings.")

# --- SESSION STATE SETUP ---
# Remember clicks across app reloads. Depot is set to an Aramex/Noon facility near Dubai Marina.
if "stops" not in st.session_state:
    st.session_state.stops = [{'lat': 25.0750, 'lon': 55.1450, 'name': 'Depot'}]

# --- FUNCTIONS ---
def get_osrm_matrix(stops):
    """Calls OSRM API to get actual driving distances and sanitizes them for OR-Tools."""
    coords = ";".join([f"{stop['lon']},{stop['lat']}" for stop in stops])
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
    
    response = requests.get(url).json()
    raw_matrix = response['distances']
    
    # OR-Tools STRICTLY requires integers. We must sanitize the OSRM floats.
    clean_matrix = []
    for row in raw_matrix:
        clean_row = []
        for val in row:
            if val is None:
                # If OSRM can't find a route between two specific points, assign a massive penalty
                clean_row.append(9999999) 
            else:
                clean_row.append(int(val))
        clean_matrix.append(clean_row)
        
    return clean_matrix

def get_osrm_route_geometry(stops, indices):
    """Fetches exact turn-by-turn road geometry leg-by-leg to prevent OSRM from skipping stops."""
    full_coords = []
    total_distance = 0
    
    # Loop through the sequence one segment at a time
    for i in range(len(indices) - 1):
        start = stops[indices[i]]
        end = stops[indices[i+1]]
        
        # Request route for just this single leg
        url = f"http://router.project-osrm.org/route/v1/driving/{start['lon']},{start['lat']};{end['lon']},{end['lat']}?overview=full&geometries=geojson"
        response = requests.get(url).json()
        
        if response.get('code') == 'Ok':
            # Add this specific leg's distance to the total
            total_distance += response['routes'][0]['distance']
            
            # Extract geometry for this leg
            geometry = response['routes'][0]['geometry']['coordinates']
            leg_coords = [[lat, lon] for lon, lat in geometry]
            
            # Combine coordinates into the master list (avoiding duplicate points at the stop itself)
            if full_coords:
                full_coords.extend(leg_coords[1:])
            else:
                full_coords.extend(leg_coords)
                
    return full_coords, total_distance

def solve_vrp(distance_matrix):
    """Runs Google OR-Tools to find the shortest possible route."""
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        route_indices = []
        while not routing.IsEnd(index):
            route_indices.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route_indices.append(manager.IndexToNode(index))
        return route_indices
    return None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Interactive Map")
    # 1. Initialize Map
    m = folium.Map(location=[25.0750, 55.1450], zoom_start=13, tiles='CartoDB positron')

    # 2. Plot Current Stops
    for i, stop in enumerate(st.session_state.stops):
        color = "black" if i == 0 else "orange"
        icon = "building" if i == 0 else "box"
        folium.Marker(
            [stop['lat'], stop['lon']], 
            popup=stop['name'],
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)

    # 3. Render Map and Capture Clicks
    map_data = st_folium(m, use_container_width=True, height=400)

    # 4. Handle New Clicks
    if map_data['last_clicked']:
        new_lat = map_data['last_clicked']['lat']
        new_lng = map_data['last_clicked']['lng']
        
        # Check if the click is new to avoid duplicate processing
        if (new_lat, new_lng) != (st.session_state.stops[-1]['lat'], st.session_state.stops[-1]['lon']):
            st.session_state.stops.append({'lat': new_lat, 'lon': new_lng, 'name': f'Stop {len(st.session_state.stops)}'})
            st.rerun()
            
    # 5. Create a placeholder for the final optimized map to appear BELOW the interactive map
    final_map_container = st.empty()

with col2:
    st.subheader("⚙️ Control Panel")
    if st.button("🗑️ Clear Map"):
        st.session_state.stops = [{'lat': 25.0750, 'lon': 55.1450, 'name': 'Depot'}]
        st.rerun()

    if len(st.session_state.stops) > 3:
        if st.button("🚀 Run Optimization Engine"):
            with st.spinner("Fetching road networks and solving VRP..."):
                
                # 1. Get real driving distances
                dist_matrix = get_osrm_matrix(st.session_state.stops)
                
                # 2. Run OR-Tools Optimization
                optimized_indices = solve_vrp(dist_matrix)
                
                if optimized_indices:
                    # 3. Create the Naive sequence (just the order they were clicked)
                    naive_indices = list(range(len(st.session_state.stops))) + [0]
                    
                    # 4. Fetch the actual road paths from OSRM
                    opt_road_coords, opt_dist_meters = get_osrm_route_geometry(st.session_state.stops, optimized_indices)
                    naive_road_coords, naive_dist_meters = get_osrm_route_geometry(st.session_state.stops, naive_indices)

                    # --- TASK 2.6: SAVINGS REPORT MATH ---
                    naive_dist_km = naive_dist_meters / 1000
                    opt_dist_km = opt_dist_meters / 1000
                    
                    fuel_price_aed = 3.00 # AED per liter for Special 95
                    van_efficiency = 8.0 # km per liter
                    
                    naive_cost = (naive_dist_km / van_efficiency) * fuel_price_aed
                    opt_cost = (opt_dist_km / van_efficiency) * fuel_price_aed
                    
                    savings_aed = naive_cost - opt_cost
                    reduction_pct = ((naive_dist_km - opt_dist_km) / naive_dist_km) * 100 if naive_dist_km > 0 else 0

                    st.success("Optimization Complete!")
                    
                    # --- RENDER THE ROI METRICS ---
                    st.markdown("### 📊 ROI Dashboard")
                    st.metric("Naive Route Distance", f"{naive_dist_km:.2f} km")
                    st.metric("Optimized Distance", f"{opt_dist_km:.2f} km", f"-{reduction_pct:.1f}% reduction")
                    st.metric("Estimated Fuel Savings", f"{savings_aed:.2f} AED")
                    
                    # --- DRAW THE FINAL MAP ---
                    m_final = folium.Map(location=[25.0750, 55.1450], zoom_start=13, tiles='CartoDB positron')
                    
                    # Plot Naive (Red) hugging the actual roads
                    folium.PolyLine(naive_road_coords, color='red', weight=3, opacity=0.4, dash_array='5, 5', tooltip="Naive Route").add_to(m_final)
                    
                    # Plot Optimized (Blue AntPath) hugging the actual roads!
                    plugins.AntPath(opt_road_coords, color='blue', weight=5, opacity=0.8, delay=1000, tooltip="Optimized Route").add_to(m_final)
                    
                    # Plot Stops
                    for i, stop in enumerate(st.session_state.stops):
                        color = "black" if i == 0 else "orange"
                        folium.Marker([stop['lat'], stop['lon']], icon=folium.Icon(color=color)).add_to(m_final)
                    
                    with final_map_container.container():
                        st.subheader("✅ Optimized Real-Road Route")
                        st_folium(m_final, use_container_width=True, height=400, returned_objects=[])
