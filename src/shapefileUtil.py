import shapefile as shp
from pathSegment import Path
from config import CONFIG


class ShapeType(object):
    ALL = ""  # 174974 records

    BRIDLEWAY = "bridleway"  # 4 records

    CONSTRUCTION = "construction"  # 310 records
    CYCLEWAY = "cycleway"  # 252 records

    ELEVATOR = "elevator"  # 4 records

    FOOTWAY = "footway"  # 5762 records

    LIVING_STREET = "living_street"  # 3542 records

    MOTORWAY = "motorway"  # 812 records
    MOTORWAY_LINK = "motorway_link"  # 2062

    PATH = "path"  # 1794 records
    PEDESTRIAN = "pedestrian"  # 378 records
    PLANNED = "planned"  # 4 records
    PRIMARY = "primary"  # 3678 records
    PRIMARY_LINK = "primary_link"  # 1938 records
    PROPOSED = "proposed"  # 4 records

    RACEWAY = "raceway"  # 14 records
    RESIDENTIAL = "residential"  # 120238 records
    ROAD = "road"  # 306 records

    SECONDARY = "secondary" # 2404 records
    SECONDARY_LINK = "secondary_link"  # 1304 records
    SERVICE = "service"  # 19294 records
    SERVICES = "services"  # 20 records
    STEPS = "steps"  # 1242 records

    TERTIARY = "tertiary"  # 3186 records
    TERTIARY_LINK = "tertiary_link"  # 694
    TRACK = "track"  # 1018 records
    TRUNK = "trunk"  # 594 records
    TRUNK_LINK = "trunk_link"  # 634 records

    UNCLASSIFIED = "unclassified"  # 3664 records

    TYPES = set()
    TYPES.add(BRIDLEWAY)
    TYPES.add(CONSTRUCTION)
    TYPES.add(CYCLEWAY)
    TYPES.add(ELEVATOR)
    TYPES.add(FOOTWAY)
    TYPES.add(LIVING_STREET)
    TYPES.add(MOTORWAY)
    TYPES.add(MOTORWAY_LINK)
    TYPES.add(PATH)
    TYPES.add(PEDESTRIAN)
    TYPES.add(PLANNED)
    TYPES.add(PRIMARY)
    TYPES.add(PRIMARY_LINK)
    TYPES.add(PROPOSED)
    TYPES.add(RACEWAY)
    TYPES.add(RESIDENTIAL)
    TYPES.add(ROAD)
    TYPES.add(SECONDARY)
    TYPES.add(SECONDARY_LINK)
    TYPES.add(SERVICE)
    TYPES.add(SERVICES)
    TYPES.add(STEPS)
    TYPES.add(TERTIARY)
    TYPES.add(TERTIARY_LINK)
    TYPES.add(TRACK)
    TYPES.add(TRUNK)
    TYPES.add(TRUNK_LINK)
    TYPES.add(UNCLASSIFIED)

    @classmethod
    def getAllTypes(cls):
        return [typ for typ in cls.TYPES]


class ShapeFileParser(object):

    def __init__(self, shapefile):
        """
        :param shapefile: (str) the file name of the given shape file
        :param shapeTypeIdx: (int) the index of the type store in the shape file
        """
        self.shapefile = shapefile
        self.shapeTypeIdx = CONFIG["shapefile"]["shapeTypeIndex"]
        self.intersections = None
        self.shapeReader = shp.Reader(shapefile)

    def getShapeTypePath(self, types):
        """
        Get the points of paths for the given road types.
        :param type: (list of str) the target types
        :return: a list of paths
        """
        return [sr.shape.points for sr in self.shapeReader.iterShapeRecords()
                if (sr.record[self.shapeTypeIdx] in types or ShapeType.ALL in types) and len(sr.shape.points) > 0]

    def getPathWithType(self, types):
        paths = []
        for sr in self.shapeReader.iterShapeRecords():
            curtType = sr.record[self.shapeTypeIdx]
            if (curtType in types or ShapeType.ALL in types) and len(sr.shape.points) > 0:
                paths.append(Path(curtType, sr.shape.points))
        return paths

    def getShapeRecord(self):
        return self.shapeReader.shapeRecords()
