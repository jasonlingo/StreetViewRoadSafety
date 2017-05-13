"""
This processEndPoints is used to extract end point of each road record in a shapefile.
Those end points are not necessarily all intersection points.
For more precise intersection points, please use "intersection.py".
"""


from shapefileUtil import ShapeFileParser
from shapefileUtil import ShapeType
from config import CONFIG
from util import getEndPoint
from util import getValidEndPoint
from util import removeDuplicatePoint


def preprocessEndPoints(types):
    """
    Parse the shape file, get the target road types data and store the valid end points to files.
    :param types: list of road types
    """
    shapefile = CONFIG["shapefile"]["filePath"]
    for type in types:
        print "======================="
        print "processing", type
        shapefile = ShapeFileParser(shapefile)

        print "parsing shape file"
        paths = shapefile.getShapeTypePath([type])

        endPoints = getEndPoint(paths)
        endPoints = removeDuplicatePoint(endPoints)
        print "end points: %d" % len(endPoints)

        print "getting valid points"
        endPoints = getValidEndPoint(endPoints)
        print "valid points: %d" % len(endPoints)

        # output to file
        lines = []
        for point in endPoints:
            lines.append("%s, %s\n" % (str(point[0]), str(point[1])) )

        file = open("../end_points/" + type + ".data", "a")
        file.writelines(lines)
        file.close()


if __name__ == "__main__":
    types = ShapeType.getAllTypes()
    preprocessEndPoints(types)
