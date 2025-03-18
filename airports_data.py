"""Data Handling File"""
import pandas as pd

"""----------AIRPORT DATA----------"""
airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                   "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

airports_df = pd.read_csv(airports_data, delimiter=",", names=airport_columns)

airports_df = airports_df.drop(
    ["Tz database time zone", "Type", "Source"], axis=1)

airports_df = airports_df.astype(
    {col: "string" for col in airports_df.select_dtypes(include=["object"]).columns})

# NOTE!!! I kept the city column just in case we need it. There are some rows WITHOUT values for the city column.

"""----------ROUTES DATA----------"""
airport_columns = ["Airline", "Airline ID", "Source airport", "Source airport ID",
                   "Destination airport", "Destination airport ID", "Codeshare", "Stops", "Equipment"]

routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

routes_df = pd.read_csv(routes_data, delimiter=",", names=airport_columns)
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
