import sqlite3 as SQLite
import csv
import sys

class Database:

    def __init__(self, database_name, latitude_nw = 180, longitude_nw = -180, latitude_se = 180, longitude_se = -180):
        self.database = SQLite.connect(database_name)

        self.latitude_nw = latitude_nw
        self.longitude_nw = longitude_nw
        self.latitude_se = latitude_se
        self.longitude_se = longitude_se
        self.coords = (latitude_nw, longitude_nw, latitude_se, longitude_se)

        self.cursor = self.database.cursor()

    def create_tables(self):
        self.cursor.execute('CREATE TABLE POIs(id INTEGER PRIMARY KEY, google_places_id VARCHAR(27), name VARCHAR(255), latitude DECIMAL, longitude  DECIMAL, types TEXT, weight INTEGER);')
        self.cursor.execute('CREATE TABLE types(type VARCHAR(50), weight INTEGER);')
        self.cursor.execute('CREATE TABLE circles(id INTEGER PRIMARY KEY, radius DECIMAL, latitude DECIMAl, longitude DECIMAl);')

    def add_circle(self, circle_to_add):
        if not self.circle_already_logged(circle_to_add):
            self.cursor.execute('INSERT INTO circles(radius, latitude, longitude) VALUES (?, ?, ?)', (circle_to_add.radius, circle_to_add.latitude, circle_to_add.longitude))

    def add_poi(self, poi_to_add):
        self.cursor.execute('SELECT * FROM POIs WHERE google_places_id = ?', (poi_to_add.google_places_id,) )
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('INSERT INTO POIs(google_places_id, name, latitude, longitude, types, weight) VALUES (?, ?, ?, ?, ?, ?)', (poi_to_add.google_places_id, poi_to_add.name, poi_to_add.latitude, poi_to_add.longitude, poi_to_add.type, poi_to_add.weight))


    def add_type(self, name, weight):
        self.cursor.execute('SELECT * FROM types WHERE type = ?', (name,) )
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('INSERT INTO types(type, weight) VALUES (?, ?)', (name, weight))


    def circle_already_logged(self, circle):
        self.cursor.execute('SELECT * FROM circles WHERE radius = ? AND latitude = ? AND longitude = ?', (circle.radius, circle.latitude, circle.longitude))
        if len(self.cursor.fetchall()) == 0:
            return False
        else:
            return True


    def clear_table(self, table):
        self.cursor.execute('DELETE FROM ' + table)


    def close(self):
        self.database.commit()
        self.database.close()


    def flatten(self, the_tuple):
        print([element for tupl in the_tuple for element in tupl])
        return [element for tupl in the_tuple for element in tupl]


    def get_pois_of_types(self, types):
        from POI import POI

        if type(types) is not tuple:
            types = tuple(types)

        pois_to_return = []

        for this_type in types:
            self.cursor.execute("SELECT * FROM POIs WHERE types LIKE \'%"+this_type+"%\' AND latitude <= ? AND longitude >= ? AND latitude >= ? AND longitude <= ?", self.coords)
            for row in self.cursor.fetchall():
                poi_to_add = POI(row[1], row[2], row[3], row[4], row[5], row[6])
                if poi_to_add not in pois_to_return:
                    pois_to_return.append(poi_to_add)

        return pois_to_return


    def get_pois_above_weight(self, weight, bounds = False):
        from POI import POI

        pois_to_return = []
        weight = str(weight)

        if bounds == False:
            self.cursor.execute('SELECT * FROM POIs WHERE weight > ?', (weight,))
        else:
            self.cursor.execute('SELECT * FROM POIs WHERE weight > ? AND latitude <= ? AND longitude >= ? AND latitude >= ? AND longitude <= ?', (weight, *bounds))

        all_from_db = self.cursor.fetchall()
        num_all = len(all_from_db)
        for i, row in enumerate(all_from_db):
            sys.stdout.write('\033[K\rRetrieving POI {} of {} from the database'.format(i+1, num_all))
            poi_to_add = POI(row[1], row[2], row[3], row[4], row[5], row[6])
            if poi_to_add not in pois_to_return:
                pois_to_return.append(poi_to_add)

        return pois_to_return

    def load_weights_from_file(self, filepath):
        with open(filepath) as weights_file:
            for row in csv.reader(weights_file, delimiter = ','):
                self.add_type(row[0], row[1])
