# this will handle our data for the airports
# we will use the data from the airports.csv file
# we will use the pandas library to read the data

import pandas as pd

# Airport Data
airport_columns = ["Airport ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude",
                   "Altitude", "Timezone", "DST", "Tz database time zone", "Type", "Source"]

airporsts_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

airports_df = pd.read_csv(airporsts_data, delimiter=",", names=airport_columns)
print(airports_df.head())

# Airport Routes Data
airport_columns = ["Airline", "Airline ID", "Source airport", "Source airport ID",
                   "Destination airport", "Destination airport ID", "Codeshare", "Stops", "Equipment"]

routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

routes_df = pd.read_csv(routes_data, delimiter=",", names=airport_columns)
print(routes_df.head())
