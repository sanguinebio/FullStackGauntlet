
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
