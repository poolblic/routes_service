from routes_service import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from uber.serializer import UberModelSerializer
import requests


# Create your views here.
class UberView(APIView):
    def get(self, request, format=None):
        result = requests.post('https://login.uber.com/oauth/v2/token', data={
            'code': request.GET.get('code'),
            'scope': 'profile',
            'grant_type': 'authorization_code',
            'client_id': settings.UBER_CLIENT_ID,
            'client_secret': settings.UBER_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:8000/uber/access_code'

        })
        response = result.json()

        access_token = response.get('access_token')
        result = requests.get('https://sandbox-api.uber.com/v1.2/me', headers={'authorization': 'Bearer ' + access_token})
        response = result.json()
        name = response.get('first_name') + response.get('last_name')
        email = response.get('email')

        serializer = UberModelSerializer(data={
            'name': name,
            'email': email,
            'access_token': access_token
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
