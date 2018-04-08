from django.test import TestCase
from longlat.views import LongLatView
class PointsTests(TestCase):
    def test_case(self):
        a = LongLatView()
        res = a.longlat_points('rua americo jacomino canhoto, 506', 'rua antonio blanco, 169')
        print(res)
# Create your tests here.
