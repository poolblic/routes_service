from django.test import TestCase
from destination.views import DestinationView


# Create your tests here.
class DestinationTest(TestCase):
    def test_get_route(self):
        dest = DestinationView()
        dest.get_route((-22.893528, -47.040663),(-22.893742, -47.040653),(-22.894152, -47.051060),(-22.909315, -47.086260))
        print("test_get_route Done")
        return True

