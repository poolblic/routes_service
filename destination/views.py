from rest_framework.views import APIView
from rest_framework.response import  Response
import googlemaps
import os
from uber_rides.session import Session
from uber_rides.client import UberRidesClient

# Create your views here.
class DestinationView(APIView):
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_DIRECTIONS_API_KEY'))

    def get(self, request):
        return Response("Ok")

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

        routes['originDest']['route'] = self.gmaps.directions(origin,
                                     dest,
                                     mode="transit",
                                     departure_time='now')
   
        routes['originCdest']['route'] = self.gmaps.directions(origin,
                                     destClose,
                                     mode="transit",
                                     departure_time='now')

        routes['coriginDest']['route'] = self.gmaps.directions(originClose,
                                     dest,
                                     mode="transit",
                                     departure_time='now') 
        routes['coriginCdest']['route'] = self.gmaps.directions(originClose,
                                     destClose,
                                     mode="transit",
                                     departure_time='now') 

        routes['originDest']['usesuber_start'] = False
        routes['originCdest']['usesuber_start'] = False
        routes['coriginDest']['usesuber_start'] = False
        routes['coriginCdest']['usesuber_start'] = False

        routes['coriginCdest']['usesuber_end'] = False
        routes['originCdest']['usesuber_end'] = False
        routes['coriginDest']['usesuber_end'] = False
        routes['coriginCdest']['usesuber_end'] = False

        if(routes['originDest']['route'][0]['legs'][0]['steps'][0]['duration']['value'] > 600):
                self._remove_first_walk(routes['originDest'])

        if(routes['originCdest']['route'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                self._remove_first_walk(routes['originCdest'])

        if(routes['coriginDest']['route'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                self._remove_last_walk(routes['coriginDest'])


        if(routes['coriginCdest']['route'][0]['legs'][0]['steps'][0]['distance']['value'] > 600):
                self._remove_last_walk(routes['coriginCdest'])

        self._remove_first_walk(routes['coriginDest'])
        self._remove_first_walk(routes['coriginCdest'])

        self._remove_last_walk(routes['originDest'])
        self._remove_last_walk(routes['originCdest'])
        
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
