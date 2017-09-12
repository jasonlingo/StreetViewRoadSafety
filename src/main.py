import random
from config import CONFIG
from csv_utils import outputCSV
from util import readPointFile
from util import Progress
from util import plotSampledPointMap
from googleStreetView import GoogleStreetView


def sampling():
    """
    The main function of the sampling process.
    :return:
    """

    # Get preprocessed point data
    intersectionPointFile = CONFIG["shapefile"]["intersectoinPointFile"]
    pointInfoFile = CONFIG["shapefile"]["pointInfoFilename"]

    pointInfo = readPointFile(pointInfoFile)
    intersectionPointInfo = readIntersectionPointInfo(intersectionPointFile)

    # Filter point data that has street images taken within the specified period.
    maxYear = CONFIG["gmap"]["streetImageMaxYear"]
    minYear = CONFIG["gmap"]["streetImageMinYear"]
    filteredPoints = filterPointByYear(pointInfo, maxYear, minYear)

    LAT_LNG_COL_NUM = 2

    # Sample street images, the return is list of sample info
    sampleNum = CONFIG["sampling"]["sampleNum"]
    initImageNumber = CONFIG["sampling"]["initImageNumber"]
    sampleData = sampleAndGetStreetImageLinks(filteredPoints, sampleNum, initImageNumber, initImageNumber, intersectionPointInfo)

    # add field titles
    columnTitle = ["Sample Number", "Sampled Point Number", "Latitude and Longitude", "Heading", "Date", "Image Name", "Road Types", "Web Link"]
    sampleData.insert(0, columnTitle)

    # output to csv file
    outputCSV(sampleData, CONFIG["sampling"]["csvFilename"])

    # plot images map
    sampledPoints = set([divideGPS(d[LAT_LNG_COL_NUM]) for d in sampleData[1:]])
    plotSampledPointMap(list(sampledPoints), CONFIG["sampling"]["sampledPointsMapFilename"])


def getValidEndPointFromFile(roadTypes):
    validEndPoints = []
    for rdType in roadTypes:
        filename = "../end_points/%s.data" % rdType
        validEndPoints += readPointFile(filename)
    return validEndPoints


def sampleAndGetStreetImageLinks(endPoints, sampleNum, picNum, ptrNum, intersectionPointInfo):
    """
    Randomly select end points from the endPoint collection.
    For each selected end point, call Google map street view image api
    to get the street view images.
    :return:
    """
    print "sampling street images..."

    # get 2x sampled points for skipping some images that are missing its date
    sampledPoints = random.sample(endPoints, sampleNum) if sampleNum < len(endPoints) * 2 else endPoints
    sampleData = []  # store (picture number, file name, lat and lng, link to image)
    progress = Progress(10)
    headings = CONFIG["gmap"]["headings"]
    sampleNumDelta = len(headings)
    for point in sampledPoints:
        progress.printProgress()
        result = getSurroundingStreetViewLinks(point, picNum, ptrNum, intersectionPointInfo)
        sampleData += result
        picNum += sampleNumDelta
        ptrNum += 1
    print ""
    return sampleData


def getSurroundingStreetViewLinks(point, picNum, ptrNum, intersectionPointInfo):
    """
    Call Google street view image api to get the links for the four surrounding images at the
    given point.
    :param point: (float, float) longitude and latitude
    :param directory: the directory for saving the images
    """
    result = []
    for heading in CONFIG["gmap"]["headings"]:
        try:
            filename = "%010d_%s_%s_%s.jpg" % (picNum, str(point[1]), str(point[0]), heading[0])
            paramDict = GoogleStreetView.makeParameterDict(point[1], point[0], heading[1])
            metadata = GoogleStreetView.getMetadata(paramDict)

            param = GoogleStreetView.makeParameter(point[1], point[0], heading[1])
            imageLink = GoogleStreetView.getStreetViewLink(param)

            if "date" in metadata:
                date = metadata["date"]
            else:
                date = "Unknown"
                print filename + " has now date"

            result.append([
                picNum,
                ptrNum,
                str(point[1]) + "," + str(point[0]),
                heading[0],
                date,
                filename,
                ",".join(intersectionPointInfo[(point[0], point[1])]),
                imageLink
            ])
            picNum += 1
        except:
            print metadata
            break
    return result


def readPointFile(filename):
    """
    The point information is retrieve from Google street view metadata API.
    Load points info from a file. Format is like
    100.619244706,13.8110460033==Actual Location:100.61920895,13.8114677028|date:2015-12

    :param filename: points filename
    :return: a dictionary of geography points and it information
    """
    pointInfo = {}
    f = open(filename, 'r')
    for data in f.readlines():
        point, info = data.split("==")
        lng, lat = [float(p) for p in point.split(",")]
        pointInfo[(lng, lat)] = parseInfoToDict(info)
    f.close()

    return pointInfo


def parseInfoToDict(info):
    infoDict = {}
    for data in info.strip("\n").split("|"):
        key, val = data.split(":")
        if key == "date":
            infoDict[key] = [int(d) for d in val.split("-")]
        else:
            infoDict[key] = val
    return infoDict


def readIntersectionPointInfo(filename):
    intersectionPointInfo = {}
    f = open(filename, 'r')
    for data in f.readlines():
        data = data.strip("\n").split("|")
        key = convertKey(data[0])
        val = data[1:]
        intersectionPointInfo[key] = val
    return intersectionPointInfo


def convertKey(lngLat):
    lng, lat = [float(p) for p in lngLat.split(",")]
    return (lng, lat)


def filterPointByYear(pointInfo, maxYear, minYear):
    points = []
    for point in pointInfo:
        if minYear <= pointInfo[point]["date"][0] <= maxYear:
            points.append(point)
    return points


def divideGPS(point):
    lat, lng = point.split(",")
    return (float(lng), float(lat))


if __name__ == "__main__":
    sampling()

