from Geometry import *
from GooglePlaces import *
from Database import *
import numpy as np

import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category = matplotlib.cbook.mplDeprecation)

#region_of_interest = (45.700860, -74.010602, 45.362423, -73.364775) # MONTREAL, LAVAL, MIRABEL & SOUTH SHORE
region_of_interest = (45.544311, -73.689637, 45.460784, -73.534160)

Database = Database('transit_planner.db', *region_of_interest)
try:
    Database.clear_table('types')
except SQLite.OperationalError:
    Database.create_tables()
Database.load_weights_from_file('weights.csv')

GooglePlaces = GooglePlaces(Database)


# Queries Google Places anew and loads results into database
def query_google_places():

    # Uncomment these next two lines as desired
    #Database.clear_table('circles')
    #Database.clear_table('POIs')

    circles = Geometry().circle_coverage(200, *region_of_interest) # MONTREAL, LAVAL, MIRABEL & SOUTH SHORE
    all_places_from_circles = GooglePlaces.get_places_from_circles(circles)


def show_plot(bounds):
    # Fetch all relevant POIs from the database
    all_pois = Database.get_pois_above_weight(0, bounds)
    print('')

    # Prepare all the coordinates
    lats = np.empty( len(all_pois) )
    lons = np.empty( len(all_pois) )
    weights = np.empty( len(all_pois) )

    for i, POI in enumerate(all_pois):
        lats[i] = POI.latitude
        lons[i] = POI.longitude
        weights[i] = POI.weight

    # Start plotting
    print('Plotting')
    plt.scatter(lons, lats, s = 2)
    plt.axes().set_aspect('equal', 'datalim')
    plt.show()


try:
    # Comment out the next line to simply plot the database
    query_google_places()
    show_plot(region_of_interest)
except KeyboardInterrupt:
    print('\nInterrupt received, stopping...\n')
finally:
    # Clean up
    Database.close()