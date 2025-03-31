"""Data Handling File for CSC111 Project 2"""
import pandas as pd
import pycountry


def load_data(airports_data_path: str, routes_data_path: str, gpi_path: str) -> tuple[
        pd.DataFrame, pd.DataFrame]:
    """Given paths to a valid airport data, routes data and Global Peace Index data, load, clean, and filter the
    datasets and return a tuple of the respective DataFrame objects in the same order.

    Preconditions:
        - airports_data_path is a valid path to a valid airports dataset from OpenFlights
        - routess_data_path is a valid path to a valid routes dataset from OpenFlights
        - gpi_path is a valid path to a valid Global Peace Index dataset from Kaggle
    """
    # ----------Airports Data----------
    airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                       "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

    airports_df = pd.read_csv(airports_data_path, delimiter=",", names=airport_columns)

    airports_df = airports_df.drop(
        ["Altitude", "IATA", "ICAO", "DST", "Tz database time zone", "Type", "Source"], axis=1)

    airports_df = airports_df.astype(
        {col: "string" for col in airports_df.select_dtypes(include=["object"]).columns})

    # Add ISO2 Data to airports_df
    countries_data_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat"
    country_columns = ["Country", "ISO2", "DAFIF"]
    countries_df = pd.read_csv(countries_data_url, delimiter=",", names=country_columns, usecols=["Country", "ISO2"])

    airports_df = airports_df.merge(countries_df[["Country", "ISO2"]], on="Country", how="left")

    # ----------Routes Data----------
    routes_columns = ["Airline", "Airline ID", "Source airport", "Source airport ID",
                      "Destination airport", "Destination airport ID", "Codeshare", "Stops", "Equipment"]

    routes_df = pd.read_csv(routes_data_path, delimiter=",", names=routes_columns)
    # Columns are not needed
    routes_df = routes_df.drop(["Airline", "Airline ID", "Equipment", "Codeshare", "Stops"], axis=1)

    # replace weird formatting where they used \N to mean NA...
    routes_df = routes_df.replace("\\N", pd.NA)

    routes_df.dropna(inplace=True)  # drop all rows with null values

    # Change data types for each column respectively
    routes_df = routes_df.astype(
        {col: "Int64" for col in routes_df if "ID" in col})
    routes_df = routes_df.astype(
        {col: "string" for col in routes_df.select_dtypes(include=["object"]).columns})

    # ----------Global Peace Index Data----------
    gpi_df = pd.read_csv(gpi_path)
    gpi_df = gpi_df.drop(["Safety and Security", "Ongoing Conflict", "Militarian"], axis=1)
    gpi_df["year"] = gpi_df["year"].astype(int)
    gpi_df = gpi_df[gpi_df["year"] == 2023]
    gpi_df.dropna(inplace=True)

    # Use pycountry to map iso3 country codes to iso2 country codes
    iso3_to_iso2 = {country.alpha_3: country.alpha_2 for country in pycountry.countries}

    # Convert iso3 country codes to iso2
    gpi_df["ISO2"] = gpi_df["iso3c"].map(iso3_to_iso2)

    # ----------FILTER DATA SO THAT ONLY AIRPORTS IN ROUTES AND AIRPORTS WHOS COUNTRY IS IN GLOBAL PEACE INDEX DATA WILL
    # BE IN AIRPORTS DATAFRAME----------
    airports_df = airports_df[airports_df["ISO2"].isin(set(gpi_df["ISO2"]))]

    valid_airports = set(routes_df["Source airport ID"]).union(set(routes_df["Destination airport ID"]))
    airports_df = airports_df[airports_df["Airport ID"].isin(valid_airports)]

    # ----------APPEND THE GPI INDEX FOR EACH AIRPORT----------
    airports_df = airports_df.merge(gpi_df[["ISO2", "Overall Scores"]], on="ISO2", how="left")
    airports_df.rename(columns={"Overall Scores": "Global Peace Index"}, inplace=True)

    return airports_df, routes_df


if __name__ == "__main__":
    # import doctest
    #
    # doctest.testmod()
    #
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ["pandas", "pycountry"],
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    # irports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    airports_data = "data/airports_small.dat"

    # routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
    routes_data = "data/routes_small.dat"

    gpi_data = "data/Global Peace Index 2023.csv"

    my_airports_df, my_routes_df = load_data(airports_data, routes_data, gpi_data)

    print(my_airports_df.head())
    print(my_routes_df.head())
