from GooglePlaces import *
from math import radians, asin, sqrt, sin, cos


class Circle:

    def __init__(self, radius, latitude, longitude):
        self.radius = radius
        self.latitude = latitude
        self.longitude = longitude


class Geometry:

    def haversine(self, latitude_a, longitude_a, latitude_b, longitude_b):
        radius_of_earth = 6.3781 * 10**6

        def hav(a, b):
            return sin((b - a) / 2) ** 2

        latitude_a = radians(latitude_a)
        longitude_a = radians(longitude_a)
        latitude_b = radians(latitude_b)
        longitude_b = radians(longitude_b)

        radicand = hav(latitude_a, latitude_b) + cos(latitude_a) * cos(latitude_b) * hav(longitude_a, longitude_b)
        return 2 * radius_of_earth * asin( sqrt(radicand) )

    def circle_coverage(self, radius, latitude_nw, longitude_nw, latitude_se, longitude_se):
        region_width = self.haversine(latitude_nw, longitude_nw, latitude_nw, longitude_se)
        #print(region_width)
        region_height = self.haversine(latitude_nw, longitude_nw, latitude_se, longitude_nw)
        current_x = 0
        current_y = 0
        current_row = 0

        circles = []

        while current_y < region_height:
            offset = 0 if current_row % 2 ==0 else sqrt(3)/2 * radius
            while current_x < region_width:
                this_latitude = latitude_nw + (latitude_se - latitude_nw) * (current_y / region_height)
                this_longitude = longitude_nw + (longitude_se - longitude_nw) * (current_x / region_width)
                circles.append( Circle(radius, this_latitude, this_longitude) )
                current_x += sqrt(3) * radius
            current_x = 0
            current_y += 3/2 * radius
            current_row += 1

        return circles
