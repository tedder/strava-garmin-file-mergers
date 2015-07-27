#!/usr/local/bin/python3

import xml.etree.ElementTree as ET
import sys
from scipy import stats
import numpy as np

print("first file: " + sys.argv[1])
#rootA = ET.parse(sys.argv[1]).getroot()
rootAactual = ET.parse(sys.argv[1])
rootA = rootAactual.getroot()
rootB = ET.parse(sys.argv[2])

def leastsq(ar1, ar2, offset = 0):
  diff = 0.0
  comps = 0
  for eindex, e in enumerate(ar1):
    bOffset = abs(offset + eindex)
    #print("bo:", bOffset, "bLen:", len(ar2))
    if e is None:
      raise BaseException("e is None" + str(e))
    if bOffset > (len(ar2) - 1) or bOffset < 0:
      break
    eB = ar2[bOffset]
    diff += (e - eB)**2
    comps += 1
  #print("comps", comps)
  if(comps < len(ar2)*0.9):
    return None

  return diff

  #slope, intercept, r_value, p_value, std_err = stats.linregress(ar1, ar2)
  #rsq = r_value**2
  #print("rsq:", rsq)

eleArray = []
count = 0
for child in rootA.iter('{http://www.topografix.com/GPX/1/1}trkpt'): #('trkseg'):
  #print("ch", child.tag, "/", child.attrib)
  time = child.find('{http://www.topografix.com/GPX/1/1}time').text
  ele = 0
  elevation_element = child.find('{http://www.topografix.com/GPX/1/1}ele')
  if elevation_element is not None:
    ele = float(elevation_element.text)

  
  lat = child.attrib.get('lat')
  lon = child.attrib.get('lon')
  eleArray.append(ele)

  #print(time, lat, lon, ele)

eleBArray = []
for child in rootB.iter('{http://www.topografix.com/GPX/1/1}trkpt'): #('trkseg'):
  #print("ch", child.tag, "/", child.attrib)
  time = child.find('{http://www.topografix.com/GPX/1/1}time').text
  ele = 0
  elevation_element = child.find('{http://www.topografix.com/GPX/1/1}ele')
  if elevation_element is not None:
    ele = float(elevation_element.text)

  
  lat = float(child.attrib.get('lat'))
  lon = float(child.attrib.get('lon'))
  ext = child.find('{http://www.topografix.com/GPX/1/1}extensions')
  #print(type(ext))
  

  eleBArray.append(ele)

  #print(time, lat, lon, ele)



#print("rsq:", leastsq(eleArray, eleBArray))
maxOffset = len(eleArray) - len(eleBArray)
fit = ()
for x in range(0, maxOffset, 10):
  rsq = leastsq(eleArray, eleBArray, x)
  #print("rsq:", x, rsq)
  if rsq is not None and (not fit or fit[0] > rsq):
    fit = (rsq, x)

print("best fit: ", fit[1], "/", fit[0])
fitOffset = fit[1]

rootBchildren = list(rootB.iter('{http://www.topografix.com/GPX/1/1}trkpt'))
print("start in b:", len(rootBchildren))

eleArray = []
upperLeft = None
lowerRight = None
for childCount, child in enumerate(rootA.iter('{http://www.topografix.com/GPX/1/1}trkpt')): #('trkseg'):
  if childCount > fitOffset and len(rootBchildren) > 0:
    b = rootBchildren.pop(0)
    child.attrib['lat'] = b.attrib.get('lat')
    child.attrib['lon'] = b.attrib.get('lon')
    ext = b.find('{http://www.topografix.com/GPX/1/1}extensions')
    child.append(ext)
    print(child.find('{http://www.topografix.com/GPX/1/1}time').text, b.find('{http://www.topografix.com/GPX/1/1}time').text)
  elif childCount > fitOffset:
    if 'lat' in child.attrib:
      del child.attrib['lat']
    if 'lon' in child.attrib:
      del child.attrib['lon']

  if child.attrib.get('lat') and child.attrib.get('lon'):
    lat = float(child.attrib.get('lat'))
    lon = float(child.attrib.get('lon'))
    if not upperLeft or (lat > upperLeft[0] and abs(lon) > abs(upperLeft[1])):
      upperLeft = (lat, lon)
    if not lowerRight or (lat < lowerRight[0] and abs(lon) < abs(lowerRight[1])):
      lowerRight = (lat, lon)

print("leftovers in b:", len(rootBchildren))
print(upperLeft, lowerRight)

#with open('merged.gpx', 'w') as f:
#  f.write(ET.tostring(rootA, encoding="unicode"))
ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
ET.register_namespace('gpxtpx', "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
rootAactual.write('merged.gpx')
