"""Data Handling File"""
import pandas as pd

"""----------AIRPORT DATA----------"""
airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                   "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
# airports_data = "data/airports_small.dat"

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

# routes_data = "data/routes_small.dat"

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

"""----------FILTER DATA SO THAT ONLY AIRPORTS IN ROUTES WILL BE IN AIRPORTS DATAFRAME----------"""
valid_airport_ids = set(routes_df["Source airport ID"]).union(set(routes_df["Destination airport ID"]))
airports_df = airports_df[airports_df["Airport ID"].isin(valid_airport_ids)]

"""----------COST OF LIVING DATA----------"""
# TODO: Maybe add this as graph edge or weighted vertex

if __name__ == "__main__":
    print(airports_df.shape)
    print(routes_df.shape)

    # with open("countries.txt", "w", encoding="utf-8") as file:
    #     for country in sorted(airports_df["Country"].unique()):
    #         file.write(country + "\n")
