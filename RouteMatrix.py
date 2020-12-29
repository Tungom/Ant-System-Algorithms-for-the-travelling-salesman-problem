import math 

# calculate distance between cities
def distance(city1: dict, city2: dict):
    return math.sqrt((city1['x'] - city2['x']) ** 2 + (city1['y'] - city2['y']) ** 2)

# calculate the Travwlling Saleman route matrix 
def TSRM(filepath):
    """ filepath is a string with the directory
    of the file conatining the routes """
    
    cities = []
    points = []
    with open(filepath) as f:
        for line in f.readlines():
            city = line.split(' ')
            cities.append(dict(index=float(city[0]), x=float(city[1]), y=float(city[2])))
            points.append((float(city[1]), float(city[2])))
    cost_matrix = []
    rank = len(cities)
    for i in range(rank):
        row = []
        for j in range(rank):
            row.append(distance(cities[i], cities[j]))
        cost_matrix.append(row)
    return cost_matrix