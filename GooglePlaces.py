from POI import *
import json
import urllib.request
from time import sleep
import sys

class GooglePlaces:

    api_key = 'YOUR_API_KEY'

    def __init__(self, Database, pagetoken_delay = 2.02, verbose = False):
        self.Database = Database
        self.pagetoken_delay = pagetoken_delay
        self.verbose = verbose


    def retrieve_json(self, url_string):
        while True:
            try:
                with urllib.request.urlopen(url_string) as url:
                    data = json.loads( url.read().decode('utf-8') )
                    if data['status'] == 'INVALID_REQUEST':
                        print('RIP')
                    return data # Returns dictionary of response
            except (urllib.error.URLError, ConnectionResetError):
                sleep(10)



    def get_places_from_radius(self, radius, latitude, longitude):
        pois_to_return = []

        url_string = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?radius='+str(radius)+'&location='+str(latitude)+','+str(longitude)+'&key='+self.api_key
        response = self.retrieve_json(url_string)

        for poi in response['results']:
            #print('Found {}'.format(poi['name']))
            poi_to_add = POI(poi['place_id'], poi['name'], poi['geometry']['location']['lat'], poi['geometry']['location']['lng'], poi['types'])
            pois_to_return.append(poi_to_add)
            self.Database.add_poi(poi_to_add)

        if 'next_page_token' in response and response['next_page_token'] != '':
            sleep(self.pagetoken_delay)
            places_from_pagetoken = self.get_places_from_pagetoken( response['next_page_token'], False )
            if places_from_pagetoken == -1:
                return -1
            else:
                pois_to_return += places_from_pagetoken

        return pois_to_return



    def get_places_from_pagetoken(self, pagetoken, should_be_final):
        pois_to_return = []

        url_string = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken='+pagetoken+'&key='+self.api_key
        response = self.retrieve_json(url_string)

        if should_be_final and len(response['results']) == 20:
            return -1 # Need to subdivide
        elif not should_be_final and 'next_page_token' in response and response['next_page_token'] != '':
            sleep(self.pagetoken_delay)
            places_from_pagetoken = self.get_places_from_pagetoken(response['next_page_token'], True)
            if places_from_pagetoken == -1:
                return -1
            else:
                pois_to_return += places_from_pagetoken
        else:
            for poi in response['results']:
                #print('Found {}'.format(poi['name']))
                poi_to_add = POI(poi['place_id'], poi['name'], poi['geometry']['location']['lat'], poi['geometry']['location']['lng'], poi['types'])
                pois_to_return.append(poi_to_add)
                self.Database.add_poi(poi_to_add)

        return pois_to_return


    def get_dense_place_set(self, latitude, longitude):
        pois_to_return = []

        for _ in range(20):
            pois_to_return.append( POI(-1, 'Dense', latitude, longitude, 'dense_type') )

        return pois_to_return



    def get_places_from_circles(self, circles, radius_subdivision_factor = 4, depth = 0, force_all_circles = False):
        from Geometry import Geometry
        Geometry = Geometry()

        pois_to_return = []

        for i, circle in enumerate(circles):
            if not self.Database.circle_already_logged(circle) and not force_all_circles:
                places_from_radius = self.get_places_from_radius( circle.radius, circle.latitude, circle.longitude )

                if places_from_radius == -1: # Need to subdivide
                    new_radius = circle.radius / radius_subdivision_factor
                    if new_radius > 10:
                        region_width = Geometry.haversine(circles[0].latitude, circles[0].longitude, circles[0].latitude, circles[-1].longitude)
                        region_height = Geometry.haversine(circles[0].latitude, circles[0].longitude, circles[-1].latitude, circles[0].longitude)

                        current_x = Geometry.haversine(circles[0].latitude, circles[0].longitude, circles[0].latitude, circle.longitude) # in metres
                        current_y = Geometry.haversine(circles[0].latitude, circles[0].longitude, circle.latitude, circles[0].longitude) # in metres

                        new_latitude_nw = circles[0].latitude + (circles[-1].latitude - circles[0].latitude) * ((current_y - circle.radius) / region_height)
                        new_longitutde_nw = circles[0].longitude + (circles[-1].longitude - circles[0].longitude) * ((current_x - circle.radius) / region_width)
                        new_latitude_se = circles[0].latitude + (circles[-1].latitude - circles[0].latitude) * ((current_y + circle.radius) / region_height)
                        new_longitutde_se = circles[0].longitude + (circles[-1].longitude - circles[0].longitude) * ((current_x + (3/2) * circle.radius) / region_width)

                        sub_circles = Geometry.circle_coverage( new_radius, new_latitude_nw, new_longitutde_nw, new_latitude_se, new_longitutde_se)
                        pois_to_return += self.get_places_from_circles(sub_circles, depth = depth + 1)
                    else:
                        pois_to_return += self.get_dense_place_set(circle.latitude, circle.longitude)
                else:
                    pois_to_return += places_from_radius

                self.Database.add_circle(circle)

                #sys.stdout.write('\033[K\rSearching circle {} of {} (depth {})'.format(i+1, len(circles), depth))
                sys.stdout.write('Searching circle {} of {} (depth {})\n'.format(i+1, len(circles), depth))
            else:
                #sys.stdout.write('\033[K\rCircle {} of {} already logged'.format(i+1, len(circles)))
                sys.stdout.write('\rCircle {} of {} already logged'.format(i+1, len(circles)))

        return pois_to_return
