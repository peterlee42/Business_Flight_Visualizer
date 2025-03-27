"""Data Handling File"""
import pandas as pd


def load_airport_and_route_data(airports_data_path: str, routes_data_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Given paths to a valid airport data and routes data, load, clean, and filter the datasets and return a tuple
    of DataFrame objects. First index being the Dataframe for airports data and second index being the DataFrame object
    for routes data.

    Preconditions:
    - airports_data_path is a valid path to a valid airports dataset from OpenFlights
    - routess_data_path is a valid path to a valid routes dataset from OpenFlights
    """

    # ----------Airports Data----------
    airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                       "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

    airports_df = pd.read_csv(airports_data_path, delimiter=",", names=airport_columns)

    airports_df = airports_df.drop(
        ["Tz database time zone", "Type", "Source"], axis=1)

    airports_df = airports_df.astype(
        {col: "string" for col in airports_df.select_dtypes(include=["object"]).columns})

    # NOTE!!! I kept the city column just in case we need it. There are some rows WITHOUT values for the city column.

    # ----------Routes Data----------
    routes_columns = ["Airline", "Airline ID", "Source airport", "Source airport ID",
                      "Destination airport", "Destination airport ID", "Codeshare", "Stops", "Equipment"]

    routes_df = pd.read_csv(routes_data_path, delimiter=",", names=routes_columns)
    # Columns are not needed
    routes_df = routes_df.drop(["Equipment", "Codeshare"], axis=1)

    # replace weird formatting where they used \N to mean NA...
    routes_df = routes_df.replace("\\N", pd.NA)

    routes_df.dropna(inplace=True)  # drop all rows with null values

    # Change data types for each column respectively
    routes_df = routes_df.astype(
        {col: "Int64" for col in routes_df if "ID" in col})
    routes_df = routes_df.astype(
        {col: "string" for col in routes_df.select_dtypes(include=["object"]).columns})

    # ----------FILTER DATA SO THAT ONLY AIRPORTS IN ROUTES WILL BE IN AIRPORTS DATAFRAME----------
    valid_airport_ids = set(routes_df["Source airport ID"]).union(set(routes_df["Destination airport ID"]))
    airports_df = airports_df[airports_df["Airport ID"].isin(valid_airport_ids)]

    return airports_df, routes_df


"""----------COST OF LIVING DATA----------"""
# TODO: Maybe add this as graph edge or weighted vertex

if __name__ == "__main__":
    airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    # airports_data = "data/airports_small.dat"

    routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
    # routes_data = "data/routes_small.dat"

    my_airports_df, my_routes_df = load_airport_and_route_data(airports_data, routes_data)

    print(my_airports_df.shape)
    print(my_routes_df.shape)
