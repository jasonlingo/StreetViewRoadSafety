# Street View Road Safety
Use Google street view images to assist the research of road safety. Extract the coordinates of intersections of a city and use them to retrieve street view images from the Google map API. For each interaction, get the multiple images that cover the 360 degree view at the center of the intersection. 

## Sampling Procedure
### Pre-processing
- parse shapefiles and determine intersection points: *intersection.py*
    - For those shapefiles that don't provide intersection information, a method is described and implemented to determine intersections from the roads' points. See [Determine road intersections](https://github.com/jasonlingo/StreetViewRoadSafety/blob/master/Determine%20road%20intersections.pdf) for details.
- Use Google Street View metadata API to get road point information (e.g. if street view photo available, photo taken date...): *checkPointInfo.py*
### Sampling procedure
- *main.py*


- Shapefile downloaded from following websites:
  - [OSM extracts for Bangkok](http://download.bbbike.org/osm/bbbike/Bangkok/)
  - [http://download.geofabrik.de/asia/thailand.html](http://download.geofabrik.de/asia/thailand.html)
  - [https://mapzen.com/data/metro-extracts/metro/bangkok_thailand/](https://mapzen.com/data/metro-extracts/metro/bangkok_thailand/)

- Tools:
  - [Shape file parser(visualizing the map)](http://mapshaper.org/)


## Program requirements
- Python Version: 2.7.9
- You'll need to install some dependent packages. Also, You'll need to fill in the Google API information in **config/config.yaml**.
