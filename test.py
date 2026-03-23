import gc
import timeit

from airports_data import load_data
from main import load_airports_graph

airports_data = "data/airports.csv"
routes_data = "data/routes.csv"
gpi_data = "data/Global Peace Index 2023.csv"

airports_df, routes_df = load_data(airports_data, routes_data, gpi_data)
g = load_airports_graph(airports_df, routes_df)

# Grab 3 real IDs directly from the graph — guaranteed to exist
all_ids = list(g._vertices.keys())
assert len(all_ids) >= 3, "Graph has fewer than 3 airports"
attendees = all_ids[:3]

print(f"Using airport IDs: {attendees}")
print(f"Names: {g.get_airport_names_from_id(attendees)}")

MAX_DIST = 5000
NUMBER = 200
TRIALS = 100
connected_times = []
adjacent_times = []

# warm up
g.get_close_airports_connected(attendees, MAX_DIST)
g.get_close_airports_connected(attendees, MAX_DIST)

gc.disable()
for trial in range(TRIALS):
    t1 = timeit.timeit(
        lambda: g.get_close_airports_connected(attendees, MAX_DIST), number=NUMBER
    )
    t2 = timeit.timeit(
        lambda: g.get_close_airports_adjacent(attendees, MAX_DIST), number=NUMBER
    )
    connected_times.append(t1 / NUMBER * 1000)
    adjacent_times.append(t2 / NUMBER * 1000)
    print(
        f"Trial {trial + 1}: connected={connected_times[-1]:.2f}ms  adjacent={adjacent_times[-1]:.2f}ms"
    )
gc.enable()


print(
    f"\nDFS connected:    avg={sum(connected_times) / TRIALS:.2f}ms  min={min(connected_times):.2f}ms  max={max(connected_times):.2f}ms"
)
print(
    f"Adjacent (naive): avg={sum(adjacent_times) / TRIALS:.2f}ms  min={min(adjacent_times):.2f}ms  max={max(adjacent_times):.2f}ms"
)
