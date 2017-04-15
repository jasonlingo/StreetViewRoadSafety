"""
These functions are used to draw the map according to a shape file.
However, it is currently broken. Can use http://mapshaper.org/ to draw the shapefile.
"""

import os
import sys
import webbrowser
import pygmaps
from shapefileUtil import ShapeFileParser
from shapefileUtil import ShapeType
from util import CustomedProgress
from config import CONFIG


def drawShapefile(filename):
    print "Draw shapefile..."
    shp = ShapeFileParser(filename)

    types = []
    types.append(ShapeType.ALL)

    allPaths = shp.getPathWithType(types)
    plotMap(allPaths)


def plotMap(allPaths):
    print "Plot points..., total %d points" % len(allPaths)

    def printFunc(n):
        sys.stdout.write("\r%d" % n)
    prog = CustomedProgress()
    prog.setThreshold(1000)
    prog.setPrintFunc(printFunc)

    centerLng, centerLat = findCenterFromPaths(allPaths)
    myMap = pygmaps.maps(centerLat, centerLng, 10)

    colors = ["#ff3300", "#3333ff", "#0000", "#ff00ff", "#00e600", "#ff9900", "#66c2ff", "#ffff00"]
    colorIdx = 0
    for path in allPaths:
        prog.printProgress()
        pathPoint = getPath(path)
        myMap.addpath(pathPoint, colors[colorIdx])
        colorIdx = (colorIdx + 1) % len(colors)

    # create map file
    mapFilename = "allPath.html"
    myMap.draw('./' + mapFilename)

    # Open the map file on a web browser.
    url = "file://" + os.getcwd() + "/" + mapFilename
    webbrowser.open_new(url)


def findCenterFromPaths(allPaths):
    maxLat = maxLng = -sys.maxint
    minLat = minLng = sys.maxint
    for path in allPaths:
        for point in path.points:
            maxLat = max(maxLat, point[1])
            maxLng = max(maxLng, point[0])
            minLat = min(minLat, point[1])
            minLng = min(minLng, point[0])
    centerLat = (minLat + maxLat) / 2.0
    centerLng = (minLng + maxLng) / 2.0
    return centerLng, centerLat


def getPath(path):
    pathPoints = []
    for point in path.points:
        pathPoints.append((point[1], point[0]))
    return pathPoints


def getAllPathPoints(path):
    allLngs = []
    allLats = []
    for point in path:
        allLngs.append(point[0])
        allLats.append(point[1])
    return allLngs, allLats


def createMapHtmlandOpen(myMap, mapFilename):
    # create map file
    mapFilename = "%s.html" % mapFilename
    myMap.draw('./' + mapFilename)

    # Open the map file on a web browser.
    url = "file://" + os.getcwd() + "/" + mapFilename
    webbrowser.open_new(url)


if __name__=="__main__":
    filename = CONFIG["shapefile"]["filePath"]
    drawShapefile(filename)