from rest_framework.response import Response
from rest_framework.views import APIView
import googlemaps

import os

#python manage.py shell

# Create your views here.
class LongLatView(APIView):
    mykey = None
    gmaps = None
    def get(self, request):
        return Response("Ok")

    def longlat_points(self, origin, destination):
        geocode_result = self.gmaps.geocode(origin)
        origin_longlat = geocode_result[0]['geometry']['location']
        origin_lat = geocode_result[0]['geometry']['location']['lat']
        origin_long = geocode_result[0]['geometry']['location']['lng']
        geocode_result = self.gmaps.geocode(destination)
        destination_lat = geocode_result[0]['geometry']['location']['lat']
        destination_long = geocode_result[0]['geometry']['location']['lng']

        if destination_lat > origin_lat:
            destination_closer_lat = destination_lat-0.03
            origin_closer_lat = origin_lat+0.3
            if origin_lat > destination_closer_lat or origin_closer_lat > destination_closer_lat:
                origin_closer_lat = origin_lat
                destination_closer_lat = destination_lat
        else:
            destination_closer_lat = destination_lat+0.03
            origin_closer_lat = origin_lat-0.3
            if origin_lat <= destination_closer_lat or origin_closer_lat <= destination_closer_lat:
                origin_closer_lat = origin_lat
                destination_closer_long = destination_long
        if destination_long > origin_long:
            destination_closer_long = destination_long-0.03
            origin_closer_long = origin_long+0.03
            if origin_long > destination_closer_long or origin_closer_long > destination_closer_long:
                origin_closer_long = origin_long
                destination_closer_long = destination_long
        else:
            destination_closer_lat = destination_lat-0.03
            origin_closer_lat = origin_lat+0.3
            if origin_long <= destination_closer_long or origin_closer_long <= destination_closer_long:
                origin_closer_long = origin_long
                destination_closer_long = destination_long
        dict =  {'origin':(origin_lat,origin_long),
         'origin_closer':(origin_closer_lat,origin_closer_long),
         'dest':(destination_lat,destination_long),
         'dest_closer':(destination_closer_lat,destination_closer_long)}
        return dict

    def __init__(self):
        self.mykey = os.environ['GEOCODINGKEY']
        self.gmaps = googlemaps.Client(key=self.mykey)

"""
{
    data: {
        origin: {
            long: float,
            lat: float
        },
        destination: {
            long: float,
            lat: float
        }
    }
}
"""
