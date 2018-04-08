from rest_framework.views import APIView
from rest_framework.response import  Response
from longlat.views import LongLatView
import googlemaps
import os


# Create your views here.
class DestinationView(APIView):
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_DIRECTIONS_API_KEY'))

    def get(self, request):
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')

        long_lat = LongLatView()

        points = long_lat.longlat_points(origin, destination)
        return Response(self.get_route(points['origin'],
                                       points['origin_closer'],
                                       points['dest'],
                                       points['dest_closer']))

    def _remove_first_walk(self, directions):
        steps = directions[0]['legs'][0]['steps']
        if(steps != [] and steps[0]['travel_mode'] == "WALKING"):
            first_walk = steps.pop(0)
            directions[0]['legs'][0]['duration']['value'] = directions[0]['legs'][0]['duration']['value'] - first_walk['duration']['value']
            directions[0]['legs'][0]['distance']['value'] = directions[0]['legs'][0]['distance']['value'] - first_walk['distance']['value']
        return directions

    def _remove_last_walk(self, directions):
        steps = directions[0]['legs'][0]['steps']
        if(steps != [] and steps[-1]['travel_mode'] == "WALKING"):
            last_walk = steps.pop(len(steps)-1)
            directions[0]['legs'][0]['duration']['value'] = directions[0]['legs'][0]['duration']['value'] - last_walk['duration']['value']
            directions[0]['legs'][0]['distance']['value'] = directions[0]['legs'][0]['distance']['value'] - last_walk['distance']['value']
        return directions

    def get_route(self, origin, originClose, dest, destClose):

        routes = {}

        routes['originDest'] = self.gmaps.directions(origin,
                                                     dest,
                                                     mode="transit",
                                                     departure_time='now')

        routes['originCdest'] = self.gmaps.directions(origin,
                                                      destClose,
                                                      mode="transit",
                                                      departure_time='now')

        routes['coriginDest'] = self.gmaps.directions(originClose,
                                                      dest,
                                                      mode="transit",
                                                      departure_time='now')

        routes['coriginCdest'] = self.gmaps.directions(originClose,
                                                       destClose,
                                                       mode="transit",
                                                       departure_time='now')
        print(routes)

        try:
            if(routes['originDest'][0]['legs'][0]['steps'][0]['duration']['value'] > 600):
                    self._remove_first_walk(routes['originDest'])
        except Exception:
            pass

        try:
            if(routes['originCdest'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                    self._remove_first_walk(routes['originCdest'])
        except Exception:
            pass

        try:
            if(routes['coriginDest'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                    self._remove_last_walk(routes['coriginDest'])
        except Exception:
            pass

        try:
            if(routes['coriginCdest'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                    self._remove_last_walk(routes['coriginCdest'])
        except Exception:
            pass

        try:
            self._remove_first_walk(routes['coriginDest'])
        except Exception:
            pass
        try:
            self._remove_first_walk(routes['coriginCdest'])
        except Exception:
            pass

        try:
            self._remove_last_walk(routes['originDest'])
        except Exception:
            pass
        try:
            self._remove_last_walk(routes['originCdest'])
        except Exception:
            pass

        return routes
