import math


# Read txt file and store it as coordinates list
def readFile(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                var1, var2 = line.split(' ')
                var1 = float(var1)
                var2 = float(var2)
                data.append([var1, var2])
    return data



# Calculate distance between two points
def calculateDistance(point1, point2):
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)


# Sort given list by proximity of points to one another
def sortByProximity(coordsList):
    sorted_coords = []
    visited = [False] * len(coordsList)

    # Start with the first coordinate in the list (you have to change first coord in txt file to your location to calculate based on your position)
    current = coordsList[0]
    visited[0] = True
    sorted_coords.append(current)

    # Find the closest unvisited coordinate to the current one
    while False in visited:
        closest_distance = float('inf')
        closest_index = -1
        for i in range(len(coordsList)):
            if visited[i] == False:
                distance = calculateDistance(current, coordsList[i])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = i
        current = coordsList[closest_index]
        visited[closest_index] = True
        sorted_coords.append(current)

    return sorted_coords



# Reads coordinates from file
coordList = readFile('coords.txt')

# Sorts the coordinates by proximity
sortedCoords = sortByProximity(coordList)

# Writes the sorted coordinates to a new file
with open('sortedCoords.txt', 'w') as file:
    for coord in sortedCoords:
        file.write(str(coord[0]) + ' ' + str(coord[1]) + '\n')

# Prints the sorted coordinates to the console
print("Points sorted by proximity to each other:")
print(sortedCoords)