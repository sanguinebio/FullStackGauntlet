from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render
import datetime

from models import JsonDump
from urllib import urlopen
import json
TRIES = 20

def index(request):
  data = get_api()
  google_map = get_map_url(data['locations'])
  return render(request, 'phlebotomy.html', {'data': data, 'google_map': google_map})

def get_api():
  print "called get_api"
  now = datetime.datetime.now()
  query = JsonDump.objects.all().order_by('time')
  if query:
    most_recent_entry = query[0]
    if most_recent_entry.time.hour == now.hour:
      return most_recent_entry.json
  base = 'http://devtest.sanguinebio.com/API'
  events_url = base + '?resource=e'
  distance_url = base + '?resource=s'
  users_url = base + '?resource=r'
  events = get_unreliable_url(events_url)
  locations = get_unreliable_url(distance_url)
  users = get_unreliable_url(users_url)
  data = {'events': events, 'locations': locations, 'users': users}
  JsonDump.objects.create(time=now, json=json.dumps(data))
  return data

def get_map_url(locations):
  markers = '&markers=color:blue%7Clabel:S%7C'
  lat_tot = 0
  lon_tot = 0
  for location in locations:
    coordinate = location['distance']['client']['geo']
    lat_tot += coordinate[0]
    lon_tot += coordinate[1]
    markers += str(coordinate[0]) + ',' + str(coordinate[1]) + '%7C'
  lat_center = lat_tot / len(locations) # take the average to find the center.
  lon_center = lon_tot / len(locations)
  url = 'http://maps.googleapis.com/maps/api/staticmap?center=' + str(lat_center) + ',' + str(lon_center) + '&zoom=9&size=600x300&maptype=roadmap' + markers + '&sensor=false'
  return url

def get_url(url):
  '''Get url with appropriate exception handling...
  '''
  request = urlopen(url)
  try:
    response = request.read()
  except:
    return "Error"
  return response

def get_unreliable_url(url, tries=TRIES):
  data = {}
  while tries > 0:
    request = urlopen(url)
    json_str = request.read()
    try:
      data = json.loads(json_str)
      break # if we get json succesfully, we break out of loop.
    except:
      data = None
    tries = tries - 1
  return data
