#!/usr/local/bin/python3

import xml.etree.ElementTree as ET
import sys
import dateutil.parser

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

b = list(rootB.iter('{http://www.topografix.com/GPX/1/1}trkpt'))
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


blist = list(rootB.iter('{http://www.topografix.com/GPX/1/1}trkpt'))
#print("start in b:", len(rootBchildren))
bstarted = False

for childCount, child in enumerate(rootA.iter('{http://www.topografix.com/GPX/1/1}trkpt')): #('trkseg'):
  # gotta get smart about how I handle the times, as the two files probably
  # don't have XML entries at the same timestamps. One file may record per
  # second, and the other one every few seconds. So, removing all the lat/lon
  # in between, which is dirty (it made my 60mi ride into a 8800mi ride).
  atime = dateutil.parser.parse(child.find('{http://www.topografix.com/GPX/1/1}time').text)
  if len(blist) > 0:
    btime = dateutil.parser.parse(blist[0].find('{http://www.topografix.com/GPX/1/1}time').text)

  if len(blist) > 0 and atime > btime:
    if not bstarted:
      bstarted = True
      print("start time:", atime, btime)
    b = blist.pop(0)
    child.attrib['lat'] = b.attrib.get('lat')
    child.attrib['lon'] = b.attrib.get('lon')
    ext = b.find('{http://www.topografix.com/GPX/1/1}extensions')
    child.append(ext)
    #print(child.find('{http://www.topografix.com/GPX/1/1}time').text, b.find('{http://www.topografix.com/GPX/1/1}time').text)
  elif bstarted:
    # we've started merging the 'b' file, so remove all GPS from this point on.
    if 'lat' in child.attrib:
      del child.attrib['lat']
    if 'lon' in child.attrib:
      del child.attrib['lon']

  #if child.attrib.get('lat') and child.attrib.get('lon'):
  #  lat = float(child.attrib.get('lat'))
  #  lon = float(child.attrib.get('lon'))
  #  if not upperLeft or (lat > upperLeft[0] and abs(lon) > abs(upperLeft[1])):
  #    upperLeft = (lat, lon)
  #  if not lowerRight or (lat < lowerRight[0] and abs(lon) < abs(lowerRight[1])):
  #    lowerRight = (lat, lon)

# why are there always three leftovers?
print("leftovers in b:", len(b))
#print(upperLeft, lowerRight)

#with open('merged.gpx', 'w') as f:
#  f.write(ET.tostring(rootA, encoding="unicode"))
ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
ET.register_namespace('gpxtpx', "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
rootAactual.write('merged.gpx')
