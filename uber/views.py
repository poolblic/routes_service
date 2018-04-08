from routes_service import settings
from rest_framework.views import APIView
from rest_framework.response import Response
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
        return Response(result, status=200)
