from rest_framework.response import Response
from rest_framework.views import APIView
#python manage.py shell

# Create your views here.
class LongLatView(APIView):
    def get(self, request):
        return Response("Ok")

    def longlat_points(self, address):
        return []


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
