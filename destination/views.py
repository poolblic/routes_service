from rest_framework.views import APIView
from rest_framework.response import  Response
from longlat.views import LongLatView
import googlemaps
import os
from uber_rides.session import Session
from uber_rides.client import UberRidesClient

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
        steps = directions['route'][0]['legs'][0]['steps']
        if(steps != [] and steps[0]['travel_mode'] == "WALKING"):
            first_walk = steps.pop(0)
            directions['route'][0]['legs'][0]['duration']['value'] = directions['route'][0]['legs'][0]['duration']['value'] - first_walk['duration']['value']
            directions['route'][0]['legs'][0]['distance']['value'] = directions['route'][0]['legs'][0]['distance']['value'] - first_walk['distance']['value']
            directions['usesuber_start'] = True
        return directions

    def _remove_last_walk(self, directions):
        steps = directions['route'][0]['legs'][0]['steps']
        if(steps != [] and steps[-1]['travel_mode'] == "WALKING"):
            last_walk = steps.pop(len(steps)-1)
            directions['route'][0]['legs'][0]['duration']['value'] = directions['route'][0]['legs'][0]['duration']['value'] - last_walk['duration']['value']
            directions['route'][0]['legs'][0]['distance']['value'] = directions['route'][0]['legs'][0]['distance']['value'] - last_walk['distance']['value']
            directions['usesuber_end'] = True
        return directions

    def get_complete_route(self, origin, originClose, dest, destClose, routes):
        session = Session(server_token=os.environ.get('UBER_TOKEN'))
        client = UberRidesClient(session)
        response = client.get_price_estimates(
            start_latitude=-22.814615,
            start_longitude=-47.059307,
            end_latitude=-22.846626,
            end_longitude=-47.062940,
            seat_count=1
        )

        estimate = response.json.get('prices')
        if(routes['originDest']['usesuber_start']):
            routes['originDest'].insert(0, self.add_uber_start(origin, routes['originDest']['route']))

        if(routes['originCdest']['usesuber_start']):
            routes['originCdest'].insert(0, self.add_uber_start(origin, routes['originCdest']['route']))

        if(routes['coriginDest']['usesuber_start']):
            routes['coriginDest']['route'].insert(0, self.add_uber_start(origin, routes['coriginDest']['route']))

        if(routes['coriginCdest']['usesuber_start']):
            routes['coriginCdest']['route'].insert(0, self.add_uber_start(origin, routes['originCdest']['route']))

        if(routes['originDest']['usesuber_end']):
            routes['originDest']['route'].append(self.add_uber_end(dest, routes['originDest']['route']))

        if(routes['originCdest']['usesuber_end']):
            routes['originCdest']['route'].append(self.add_uber_end(dest, routes['originCdest']['route']))

        if(routes['coriginDest']['usesuber_end']):
            routes['coriginDest']['route'].append(self.add_uber_end(dest, routes['coriginDest']['route']))

        if(routes['coriginCdest']['usesuber_end']):
            routes['coriginCdest']['route'].append(self.add_uber_end(dest, routes['originCdest']['route']))
        return routes

    def get_route(self, origin, originClose, dest, destClose):
        routes = {'originDest':{},
                  'originCdest':{},
                  'coriginDest':{},
                  'coriginCdest':{}}

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

        routes['originDest']['usesuber_start'] = False
        routes['originCdest']['usesuber_start'] = False
        routes['coriginDest']['usesuber_start'] = False
        routes['coriginCdest']['usesuber_start'] = False

        routes['coriginCdest']['usesuber_end'] = False
        routes['originCdest']['usesuber_end'] = False
        routes['coriginDest']['usesuber_end'] = False
        routes['coriginCdest']['usesuber_end'] = False

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
        
        return self.get_complete_route(origin, originClose, dest, destClose, routes)

#passar o antes do legs
    def add_uber_start(self, origin, directions):
            uberRoute = self.gmaps.directions(origin,
                                         directions[0]['legs'][0]['steps'][0]["start_location"],
                                         mode="driving",
                                         departure_time='now')
            return uberRoute[0]
 
    def add_uber_end(self, dest, directions):
            uberRoute = self.gmaps.directions(directions[0]['legs'][0]['steps'][-1]["start_location"],
                                         dest,
                                         mode="driving",
                                         departure_time='now')
            return uberRoute[0]
