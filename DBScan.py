'''
print('Starting to cluster')
DBScan = DBScan.DBScan(lons, lats, weights, 500, 500)
DBScan.db_scan()
print('Done clustering')
'''

from math import sqrt
import sys

class DBScan:

    def __init__(self, xs, ys, weights, eps, min_weight):
        self.xs = list(xs)
        self.ys = list(ys)
        self.weights = list(weights)
        if len(xs) == len(ys) == len(weights):
            self.num_points = len(xs)
        else:
            print('Xs, Ys, and weights must be of same length.')
        self.eps = eps
        self.min_weight = min_weight
        self.clusters = []
        self.noise = []

    def get_clusters(self):
        return self.clusters

    def get_noise(self):
        return self.noise

    def get_neighbours(self, this_point): # Optimize when using SQL by only comparing against nearby POIs in table
        neighbours = []
        weight = 0
        for p in range(self.num_points):
            if self.distance((self.xs[p], self.ys[p]), this_point) <= self.eps:
                neighbours.append( (self.xs[p], self.ys[p]) )
                weight += self.weights[p]
        return neighbours, weight

    def db_scan(self):
        num_clusters = -1 # Initialize as -1 not 0
        for p in range(self.num_points):
            sys.stdout.write('\rCurrently clustering {} of {}'.format(p, self.num_points))
            this_point = (self.xs[p], self.ys[p])
            if this_point in sum(self.clusters, []):
                continue
            else:
                neighbours, weight = self.get_neighbours(this_point)

                if weight < self.min_weight:
                    self.noise.append(this_point)
                    continue

                # Start new cluster
                num_clusters += 1
                self.clusters.append([])

                self.clusters[num_clusters].append(this_point)

                subset_of_neighbours = neighbours
                for neighbour in subset_of_neighbours:
                    if neighbour in self.noise:
                        self.clusters[num_clusters].append( self.noise.pop( self.noise.index(neighbour) ) )
                    elif neighbour not in self.noise and neighbour not in sum(self.clusters, []):
                        continue
                    else:
                        self.clusters[num_clusters].append(neighbour)

                        neighbours_of_neighbour, weight_of_neighbours_of_neighbour = self.get_neighbours(neighbour)
                        if weight_of_neighbours_of_neighbour >= self.min_weight:
                            subset_of_neighbours.append(neighbours_of_neighbour)

    def distance(self, point_a, point_b):
        from Geometry import Geometry
        return Geometry().haversine( point_a[0], point_a[1], point_b[0], point_b[1] )
        #return sqrt((point_b[0] - point_a[0])**2 + (point_b[1] - point_a[1])**2)
