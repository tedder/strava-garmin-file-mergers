#!/usr/local/bin/python3

import xml.etree.ElementTree as ET
import sys
import dateutil.parser
import fileinput
import re

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
  #slope, intercept, r_value, p_value, std_err = stats.linregress(ar1, ar2)
  #rsq = r_value**2
  #print("rsq:", rsq)

  return diff

def mergeB(rootA, rootB):
  blist = list(rootB.iter('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint'))
  bstarted = False

  countChild = 0
  countAppends = 0

  for childCount, child in enumerate(rootA.iter('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint')): #('trkseg'):
    if not child:
      print("wtf, no child, yo.")
      continue
    # gotta get smart about how I handle the times, as the two files probably
    # don't have XML entries at the same timestamps. One file may record per
    # second, and the other one every few seconds. So, removing all the lat/lon
    # in between, which is dirty (it made my 60mi ride into a 8800mi ride).
    atime = dateutil.parser.parse(child.find('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time').text)
    if len(blist) > 0:
      btime = dateutil.parser.parse(blist[0].find('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time').text)
    #print(atime, btime)

    if len(blist) > 0 and atime > btime:
      if not bstarted:
        bstarted = True

      b = blist.pop(0)
      posA = list(child.iter('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position'))
      extB = b.find('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Extensions')
      hrB = b.find('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm')
      if hrB:
        #print("hrb: " + hrB)
        child.append(hrB)
      if not extB:
        print("no extb")
        #child.append(hrB)
        #print("no extensions, skipping.")
      else:
        child.append(extB)
        countAppends += 1

  # why are there always three leftovers?
  print("leftovers in b:", len(b))
  #print(upperLeft, lowerRight)


# gotta do some manual steps after this runs.
#merge all lines into one, makes things easier: [lines]J
#:s/TPX:Speed/Speed/g
#:s/<TPX:TPX Cad/<TPX xmlns="http:\/\/www.garmin.com\/xmlschemas\/ActivityExtension\/v2" Cad/g
#:s/<\/TPX:TPX/<\/TPX/g

# replace <Training.. header with this:
#<?xml version="1.0" encoding="UTF-8"?><TrainingCenterDatabase xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd" xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1" xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2" xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >

print("first file: " + sys.argv[1])
#rootA = ET.parse(sys.argv[1]).getroot()
rootAactual = ET.parse(sys.argv[1])
rootA = rootAactual.getroot()

for bfile in sys.argv[2:]:
  print("next B file:" + bfile)
  rootB = ET.parse(bfile)
  mergeB(rootA, rootB)

#with open('merged.gpx', 'w') as f:
#  f.write(ET.tostring(rootA, encoding="unicode"))
ET.register_namespace('', "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
#ET.register_namespace('gpxtpx', "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
ET.register_namespace('TPX', "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
rootAactual.write('merged.tcx')

with open('merged2.tcx', 'w') as outfile:
  #for line in fileinput.input('merged.tcx', inplace=True, backup='.bak'):
  for line in open('merged.tcx', 'r'):
    line = re.sub(r'TPX:Speed', 'Speed', line)
    line = re.sub(r'<TPX:TPX Cad', '<TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2" Cad', line)
    line = re.sub('</TPX:TPX', '</TPX', line)
    # replace <Training.. header with this:
    line = re.sub(r'<TrainingCenterDatabase.*?>', '<?xml version="1.0" encoding="UTF-8"?><TrainingCenterDatabase xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd" xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1" xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2" xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', line)
    outfile.write(line)
    #print("**" + line)


