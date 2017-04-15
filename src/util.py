import os
import sys
import pygmaps
import webbrowser
import numpy as np
from math import sin, radians, cos, asin, sqrt, atan2, pi
from googleStreetView import GoogleStreetView
from config import CONFIG

EARTH_RADIUS_KM = 6371.0

class CustomedProgress(object):
    """
    Used to print the progress for a long-running process.
    """

    def __init__(self):
        self.count = 0

    def setThreshold(self, num):
        self.threshold = num

    def setPrintFunc(self, func):
        self.printFunc = func

    def printProgress(self):
        self.count += 1
        if self.count == self.threshold:
            self.printFunc(self.count)
            self.count = 0


class Logger(object):

    # default log file name
    filename = "log.txt"

    @classmethod
    def setLogFile(cls, filename):
        cls.filename = filename

    @classmethod
    def writeLog(cls, msg):
        log = open(cls.filename, 'a')
        log.write(msg + "\n")
        log.close()

    @classmethod
    def printAndWrite(cls, msg):
        print msg
        cls.writeLog(msg)


def getEndPoint(path):
    """
    Extract the end points (first and last) from each list of points
    :param path: (list of list of float)
    :return: a list of all end points
    """
    endPoints = []
    for points in path:
        endPoints.append(points[0])
        if len(points) >= 2:
            endPoints.append(points[-1])
    return endPoints


def getValidEndPoint(points):
    validPoints = []
    progress = Progress(10)
    for point in points:
        progress.printProgress()
        if isValidPoint(point):
            validPoints.append(point)
    print ""
    return validPoints


def isValidPoint(point):
    """
    Call Google Street Image View metadata API to check the existance
    of the street view image for the given point.
    :return:
    """
    headings = CONFIG["gmap"]["headings"]
    params = GoogleStreetView.makeParameterDict(point[1], point[0], headings[0][1])
    return GoogleStreetView.isValidPoint(params)


def removeDuplicatePoint(points):
    pointSet = set()
    uniquePoints = []
    for point in points:
        tuplePoints = tuple(point)
        if tuplePoints not in pointSet:
            uniquePoints.append(point)
            pointSet.add(tuplePoints)
    return uniquePoints


def getMapCenter(points):
    """
    :param points: (float, float) longitude, latitude
    :return: (lat, lng)
    """
    maxLat = maxLng = -sys.maxint
    minLat = minLng = sys.maxint
    for point in points:
        maxLat = max(maxLat, point[1])
        maxLng = max(maxLng, point[0])
        minLat = min(minLat, point[1])
        minLng = min(minLng, point[0])
    centerLat = (minLat + maxLat) / 2.0
    centerLng = (minLng + maxLng) / 2.0
    return centerLat, centerLng


def plotSampledPointMap(points, mapName):
    """
    Plot samples points to the google map.
    :param points:
    :return:
    """
    centerLat, centerLng = getMapCenter(points)
    myMap = pygmaps.maps(centerLat, centerLng, 10)
    for point in points:
        myMap.addpoint(point[1], point[0], "b")

    # create map file
    mapFilename = "../data/%s.html" % mapName
    myMap.draw('./' + mapFilename)

    # Open the map file on a web browser.
    url = "file://" + os.getcwd() + "/" + mapFilename
    webbrowser.open_new(url)


def makeDirectory(directory):
    """
    Check directory is existing. If not exist, then create it.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        sys.stderr.write("Dirctory [%s] already exists!" % directory)
        exit(1)


def readPointFile(filename):
    """
    Read points file and return them as a list of points
    :param filename:
    :return: a list of points (lng, lat)
    """
    file = open(filename, "r")
    points = []
    for line in file.readlines():
        point = [float(p.strip(",")) for p in line.split()]
        points.append(point)
    return points


class Progress(object):

    def __init__(self, frequency):
        self.count = 0
        self.freq = frequency

    def printProgress(self):
        self.count += 1
        if self.count == self.freq:
            self.count = 0
            print ".",


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Args:
      (tuple) poitn1: the position of the first point
      (tuple) point2: the position of the second point
    Return:
      (float) distance (in km) between two nodes
    """
    # Convert decimal degrees to radians
    lng1, lat1 = point1
    lng2, lat2 = point2
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))

    return c * EARTH_RADIUS_KM


def calcVectAngle(segment1, segment2):
    """
    Calculate the clock-wise angle between two vectors.
    :param vec1: (float, float) the first vector that is used as the starting point for
                 the angle.
    :param vec2: (float, float) the second vector
    """
    vec1 = getVecFromSegment(segment1)
    vec2 = getVecFromSegment(segment2)
    angle = atan2(vec1[0], vec1[1]) - atan2(vec2[0], vec2[1])
    angle = angle * 360 / (2 * pi)
    if angle < 0:
        angle += 360
    return angle


def getVecFromSegment(segment):
    p1 = np.array(segment[0])
    p2 = np.array(segment[1])
    return p1 - p2


