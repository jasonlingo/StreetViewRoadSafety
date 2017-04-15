from __future__ import division
import sys
from util import calcVectAngle
from util import haversine
from config import CONFIG


class Intersection(object):

    def __init__(self, point):
        self.point = point
        # self.pathPoints = set()
        self.segments = set()


class Path(object):

    def __init__(self, type, points):
        self.type = type
        self.points = points


class PathSegment(object):

    def __init__(self, type, point1, point2):
        self.type = type
        self.segment = (point1, point2)

    def findIntersectPoint(self, other):
        if PathSegment.isValidAngle(self.segment, other.segment):
            intersectPoint = PathSegment.lineIntersection(self.segment, other.segment)
            if intersectPoint and PathSegment.isValidIntersectionPoint(intersectPoint, self.segment, other.segment):
                return intersectPoint

    @classmethod
    def isValidAngle(cls, segment1, segment2):
        angle = calcVectAngle(segment1, segment2)
        if smallAngle(angle):
            return False
        else:
            return True

    @classmethod
    def isValidIntersectionPoint(cls, intersectionPoint, line1, line2):
        withinLine1 = PathSegment.isInTheMiddle(intersectionPoint, line1)
        withinLine2 = PathSegment.isInTheMiddle(intersectionPoint, line2)
        if withinLine1 > 0 or withinLine2 > 0:
            return nearbyPoints(intersectionPoint, line1 + line2, 0.001)
        else:
            return True

    @classmethod
    def isInTheMiddle(cls, point, line):
        middleX = (point[0] - line[0][0]) * (point[0] - line[1][0])
        middleY = (point[1] - line[0][1]) * (point[1] - line[1][1])
        if middleX > 0 or middleY > 0:
            return 1
        else:
            return -1

    @classmethod
    def lineIntersection(cls, line1, line2):
        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        div = det(xdiff, ydiff)
        if div == 0:
           return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return (x, y)


PATH_DEGREE = CONFIG["intersection"]["pathDegree"]
LIMIT_ANGLE1 = PATH_DEGREE
LIMIT_ANGLE2 = 360 - PATH_DEGREE
LIMIT_ANGLE3 = 180 - PATH_DEGREE
LIMIT_ANGLE4 = 180 + PATH_DEGREE

def smallAngle(angle):
    return angle <= LIMIT_ANGLE1 or angle >= LIMIT_ANGLE2 or (LIMIT_ANGLE3 <= angle <= LIMIT_ANGLE4)

def nearbyPoints(mainPoint, points, dist):
    nearPointNum = 0
    for point in points:
        distBetween = haversine(mainPoint, point)
        if distBetween <= dist:
            nearPointNum += 1
    if nearPointNum >= 2:
        return True
    else:
        return False


def getSegmentPoint(segment):
    points = []
    for point in segment.segment:
        points.append((point[1], point[0]))
    return points


def getMinMaxLatLng(allPaths):
    maxLat, maxLng = -sys.maxint, -sys.maxint
    minLat, minLng = sys.maxint, sys.maxint
    for path in allPaths:
        pathLngs = [point[0] for point in path.points]
        pathLats = [point[1] for point in path.points]
        maxPathLng = max(pathLngs)
        minPathLng = min(pathLngs)
        maxPathLat = max(pathLats)
        minPathLat = min(pathLats)
        maxLng = max(maxLng, maxPathLng)
        minLng = min(minLng, minPathLng)
        maxLat = max(maxLat, maxPathLat)
        minLat = min(minLat, minPathLat)
    return maxLng, minLng, maxLat, minLat