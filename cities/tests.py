import os.path

from mongoengine import connect

from unittest import TestCase

from django.conf import settings

from .management.commands.fixtures_to_mongo import Extracter
from .models import Country, Region, City, District

class TestMongoCities(TestCase):

    db_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    def setUp(self):
        connect(self.db_name)
        fixtures_dir = '%s/fixtures' % os.path.dirname(__file__) 
        fixtures_path = '%s/test_fixtures.json' % fixtures_dir
        extracter = Extracter(fixtures_path=fixtures_path)
        extracter.to_db()

    def test_london_boroughs(self):
        # asserts that
        uk = Country.objects.get(code='GB')
        # the following tests as well, that only *one* of the two londons
        # in the test-fixtures has been imported.
        london = City.objects.get(name='London', country=uk)
        boroughs = District.objects.filter(city=london)
        exp_b_slugs = sorted(((
            "woolwich",
            "wood-green",
            "west-wickham",
        )))
        b_slugs = sorted(b.slug for b in boroughs)
        self.assertEquals(b_slugs, exp_b_slugs)

    def test_distance_berlin_lonlat_NY(self):
        germany = Country.objects.get(code='DE')
        berlin = City.objects.get(name='Berlin', country=germany)
        lonlat_of_NY = ((-73.96751403808594, 40.78054143186031))
        distance = berlin.distance_to(lonlat_of_NY) 
        self.assertLessEqual(distance, 6390)
        self.assertGreaterEqual(distance, 6380)

    def test_distance_berlin_london(self):
        uk = Country.objects.get(code='GB')
        london = City.objects.get(name='London', country=uk)
        germany = Country.objects.get(code='DE')
        berlin = City.objects.get(name='Berlin', country=germany)
        distance = london.distance_to(berlin)
        self.assertLessEqual(distance, 935) 
        self.assertGreaterEqual(distance, 930) 

    def test_nearest_cities_to_london(self):
        uk = Country.objects.get(code='GB')
        london = City.objects.get(name='London', country=uk)
        found = City.near(london.location)
        found = found.filter(id__ne=london.id).order_by('distance')[:5]
        found_slugs = [c.slug for c in found]
        expected = ['berlin', 'andorra-la-vella', 'sant-julia-de-loria']
        self.assertEqual(found_slugs, expected)
