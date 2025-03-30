"""Data Handling File for CSC111 Project 2"""
import pandas as pd


def load_data(airports_data_path: str, routes_data_path: str, safety_index_path: str) -> tuple[
        pd.DataFrame, pd.DataFrame]:
    """Given paths to a valid airport data, routes data and safety index data, load, clean, and filter the datasets and
    return a tuple of the respective DataFrame objects in the same order.

    Preconditions:
        - airports_data_path is a valid path to a valid airports dataset from OpenFlights
        - routess_data_path is a valid path to a valid routes dataset from OpenFlights
        - safety_index_path is a valid path to a valid safety index dataset from worldpopulationreview
    """
    # ----------Airports Data----------
    airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                       "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

    airports_df = pd.read_csv(airports_data_path, delimiter=",", names=airport_columns)

    airports_df = airports_df.drop(
        ["IATA", "ICAO", "DST", "Tz database time zone", "Type", "Source"], axis=1)

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

    # ----------Safety Index Data----------
    safety_df = pd.read_csv(safety_index_path)

    safety_df.dropna(inplace=True)

    safety_df.rename(columns={'country': 'Country'}, inplace=True)

    # ----------FILTER DATA SO THAT ONLY AIRPORTS IN ROUTES AND AIRPORTS WHOS COUNTRY IS IN SAFETY INDEX DATA WILL BE
    # IN AIRPORTS DATAFRAME----------
    airports_df = airports_df[airports_df["Country"].isin(set(safety_df["Country"]))]

    valid_airports = set(routes_df["Source airport ID"]).union(set(routes_df["Destination airport ID"]))
    airports_df = airports_df[airports_df["Airport ID"].isin(valid_airports)]

    # ----------APPEND THE SAFETY INDICES FOR EACH AIRPORT----------
    airports_df = airports_df.merge(safety_df[["Country", "MostPeaceful2024GPI"]], on="Country", how="left")
    airports_df.rename(columns={"MostPeaceful2024GPI": "Safety Index"}, inplace=True)

    return airports_df, routes_df


if __name__ == "__main__":
    airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    # airports_data = "data/airports_small.dat"

    routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
    # routes_data = "data/routes_small.dat"

    safety_index_data = "data/safest-countries-in-the-world-2025.csv"

    my_airports_df, my_routes_df = load_data(airports_data, routes_data, safety_index_data)

    print(my_airports_df.columns)
