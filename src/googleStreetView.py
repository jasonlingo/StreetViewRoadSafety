import urllib
import json
import requests
import time
from collections import namedtuple
from config import CONFIG


class GoogleStreetView(object):

    # For passing the parameters to the API
    StreetViewParam = namedtuple("StreetViewParam", ["lat", "lng", "heading", "pov", "pitch"])

    # the api request address
    GOOGLE_API_KEY = CONFIG["gmap"]["apiKey"]
    STREET_IMAGE_API = "https://maps.googleapis.com/maps/api/streetview?" \
                             "size=640x640&" \
                             "location=%f,%f&" \
                             "heading=%f&" \
                             "pov=%f&" \
                             "pitch=%f&" \
                             "key=" + GOOGLE_API_KEY

    # the metadata request address
    METADATA_API = "https://maps.googleapis.com/maps/api/streetview/metadata?"

    # Google API query limit, query per second
    TIME_TO_PAUSE_REQUEST = 9

    queryTimes = 0

    # Google API Error code
    OVER_QUERY_LIMIT = "OVER_QUERY_LIMIT"
    OK = "OK"

    @classmethod
    def isValidPoint(cls, params):
        data = cls.getMetadata(params)
        if data["status"] == cls.OVER_QUERY_LIMIT:
            print "OVER_QUERY_LIMIT!!!"
            exit(0)
        return data["status"] == cls.OK

    @classmethod
    def getMetadata(cls, params):
        cls.timeToPause()
        response = requests.get(url=cls.METADATA_API, params=params)
        return json.loads(response.text)

    @classmethod
    def downloadStreetView(cls, params, imgPathAndFilename):
        """
        Download street view image according to the given parameters and
        store it to the given file path.
        :param params: (tuple) lat, lng, heading, pov
        :param outputName: (str) the output path and file name
        """
        cls.timeToPause()
        requestUrl = cls.STREET_IMAGE_API % params
        urllib.urlretrieve(requestUrl, imgPathAndFilename)

    @classmethod
    def timeToPause(cls):
        cls.queryTimes += 1
        if cls.queryTimes == cls.TIME_TO_PAUSE_REQUEST:
            time.sleep(1)
            cls.queryTimes = 0

    @classmethod
    def makeParameterDict(cls, lat, lng, heading, fov=90, pitch=0):
        params = dict(
            size="640x640",
            location=str(lat) + "," + str(lng),
            heading=str(heading),
            fov=str(fov),
            pitch=str(pitch),
            key=cls.GOOGLE_API_KEY
        )
        return params

    @classmethod
    def makeParameter(cls, lat, lng, heading, fov=90, pitch=0):
        """
        Make a StreetViewParam tuple according to the given values.
        There is a default value for fov and pitch. If other value

        :param lat: (float) latitude
        :param lng: (float) longitude
        :param heading: (float) the direction:
                        0 or 360 = North; 90 = East; 180 = South; 270 = West
        :param fov: (float) width of the view (0 - 120)
        :param pitch: (float) up or down angle (0 - 90)
        :return: a StreetViewParam tuple
        """
        return cls.StreetViewParam(lat, lng, heading, fov, pitch)
