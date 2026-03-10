# Dubai-Last-Mile-Delivery-Optimizer

📌 Project Overview

The Dubai Last-Mile Delivery Optimizer is an interactive Decision Support System (DSS) designed to solve the highly complex Vehicle Routing Problem (VRP). Tailored specifically for the Dubai road network (e.g., Dubai Marina, JLT, Sheikh Zayed Road), this application minimizes logistics operational expenditure (OpEx) by calculating the most efficient delivery sequences for fleet vehicles.

Rather than relying on static datasets or straight-line distances, this tool integrates with the Open Source Routing Machine (OSRM) API to snap routes to actual drivable roads, account for impossible U-turns, and generate precise, real-world fuel cost reductions in AED.

💼 Business Value & ROI

For major logistics hubs and e-commerce platforms, inefficient routing leads to inflated fuel costs and missed SLA delivery windows. This project demonstrates commercial Data Science application by:

Minimizing Travel Distance: Utilizing Google OR-Tools to escape local minimums and find globally optimized route sequences.

Calculating Direct Financial Impact: Translating algorithmic efficiency into tangible metrics (Estimated AED Fuel Savings per shift).

Real-World Constraints: Accounting for physical road layouts, divided highways, and dynamic map inputs.

🛠️ Technical Architecture & Stack

Optimization Engine: Google OR-Tools (Constraint Programming, Guided Local Search Metaheuristics)

Geospatial Routing: OSRM API (Turn-by-turn JSON geometry, real-road distance matrices)

Front-End UI/UX: Streamlit, Streamlit-Folium

Data Manipulation: Python (Pandas, NumPy)

Mapping & Visualization: Folium (AntPath animations, interactive coordinate plotting)

✨ Key Features

Interactive Geospatial UI: Users can dynamically drop delivery pins anywhere on the Dubai map to simulate custom route manifests.

Leg-by-Leg API Routing: Bypasses "impossible continuous route" errors by querying OSRM for segment-by-segment navigation, ensuring 100% accuracy in distance calculations.

Live ROI Dashboard: Automatically compares the "Naive" (chronological) route against the OR-Tools optimized route, displaying distance reduction percentages and fuel savings.

Visual Route Comparison: Renders both routes simultaneously, utilizing animated paths to clearly display the optimized flow of traffic.

🔮 Future Enhancements

Traffic Weighting: Integrate historical congestion data to penalize routes utilizing Sheikh Zayed Road during peak hours (8 AM - 10 AM).

Cloud Scalability: Migrate distance matrix generation to Google BigQuery GIS functions (ST_DISTANCE, ST_GEOGPOINT) to handle massive, city-wide node datasets.

Multi-Vehicle Fleets (CVRP): Expand the OR-Tools data model to handle Capacitated Vehicle Routing, dispatching multiple vans with package limits simultaneously.
