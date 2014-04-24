'''Comments are indicated in triple quotes or after #'s
This is the view file: index is called whenever the url is hit.
'''

from django.shortcuts import render
from django.http import HttpResponse
import datetime

from models import JsonDump
from urllib import urlopen
import json
TRIES = 20

def json_endpoint(request):
  data = get_api()
  list_list_cells = map( lambda x:
                         [x['marker'],
                          x['profile'].get('name', ""),
                          x['rating'], '<img height=100 src="' + x['profile'].get('picUrl', "") + '"></img>'],
                         data['users']
                       )

  return HttpResponse(json.dumps(list_list_cells), mimetype='application/javascript')

def index(request):
  data = get_api()
  google_map = get_gmap_url(data['locations'])
  return render(request, 'phlebotomy.html',{'data': data,'google_map': google_map, })

def get_api():
  '''Gets the necessary data from the api and stores it in the JsonDump database table.
  Given a request call to get_api at time $now$, if there is an entry in the database from the
  same hour, then we simply return that entry. Otherwise, we make a call to the url and populate
  the JsonDump database table.
  '''
  now = datetime.datetime.now()
  query = JsonDump.objects.all().order_by('time')
  if query:
    most_recent_entry = list(query)[-1] # last element is most recent b/c sorted in ascending order
    if most_recent_entry.time.hour == now.hour:
      # we return this entry instead of making a call to the api
      return json.loads(most_recent_entry.json)

  base = 'http://devtest.sanguinebio.com/API'
  events_url = base + '?resource=e'
  distance_url = base + '?resource=s'
  users_url = base + '?resource=r'

  events = get_unreliable_url(events_url)
  locations = get_unreliable_url(distance_url)
  users = try_bad_json(users_url)
  for i in range(len(users)):
    users[i]['marker'] = i # add in a marker to indicate location on the map
    ratings = map(lambda x: x['merit'], users[i]['ratings'])
    if ratings:
      users[i]['rating'] = float(sum(ratings))/len(ratings)
    else:
      users[i]['rating'] = 0.

  data = {'events': events, 'locations': locations, 'users': users}
  JsonDump.objects.create(time=now, json=json.dumps(data)) # save the data in the JsonDump database table
  return data

def get_gmap_url(locations):
  '''Creates a google maps image src url from the locations.
  '''
  lat_tot = 0
  lon_tot = 0
  markers = ''
  for i, location in enumerate(locations):
    coordinate = location['userInfo']['location']['geo']
    lat_tot += coordinate[0]
    lon_tot += coordinate[1]
    markers += '&markers=color:blue%7Clabel:' + str(i) + '%7C' + str(coordinate[0]) + ',' + str(coordinate[1]) + '%7C'
  first_geo = locations[0]['userInfo']['location']['geo']
  lat_center = first_geo[0]
  lon_center = first_geo[1]
  url = 'http://maps.googleapis.com/maps/api/staticmap?center=' + str(lat_center) + ',' + str(lon_center) + '&zoom=8&size=450x500&maptype=roadmap' + markers + '&sensor=false'
  return url

def get_unreliable_url(url, tries=TRIES):
  '''Gets json from url.
  Fails after having tried [tries] number of times.
  '''
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

def get_url(url):
  '''Get url with appropriate exception handling...
  '''
  request = urlopen(url)
  try:
    response = request.read()
  except:
    return "Error"
  return response

def try_bad_json(url, tries=TRIES):
  '''Used to get the json from the resources=r endpoint:
  http://devtest.sanguinebio.com/API?resource=r
  This endpoint does not return correctly formatted json.
  I must add commas between dictionaries and add [ and ] to make list of dicts.
  '''
  while tries > 0:
    users = get_url(url)
    if '_id' in users:
      users = '[' + users.replace('\n{"_id', ', {"_id').replace('\n', ' ') + ']' # MAKE the json valid :(
      try:
        users = json.loads(users) # MAKE it json
        break
      except:
        users = ''
      tries -= 1
  return users
