class POI:

    def __init__(self, google_places_id, name, latitude, longitude, weight_determining_type, weight = -1):
        self.google_places_id = google_places_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.type = weight_determining_type
        self.weight = weight

        if weight == -1:
            self.get_weight_determining_type()


    def get_weight_determining_type(self):
        from Database import Database
        Database = Database('transit_planner.db')

        new_type = ''
        current_max_weight = -1
        for potential_type in self.type:
            Database.cursor.execute('SELECT * FROM types WHERE type = ?', (potential_type,))
            for row in Database.cursor.fetchall():
                if row[1] > current_max_weight:
                    current_max_weight = row[1]
                    new_type = row[0]

        self.type = new_type
        self.weight = current_max_weight

        Database.close()
