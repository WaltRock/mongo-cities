from mongoengine import *
from mongoengine.queryset import queryset_manager

#from django.contrib.gis.geos import Point


class GeoManager(object):
    "Overrides Manager to return Geographic QuerySets."

    # This manager should be used for queries on related fields
    # so that geometry columns on Oracle and MySQL are selected
    # properly.
    use_for_related_fields = True

    @queryset_manager
    def get_query_set(self):
        return GeoQuerySet(self.model, using=self._db)

    @queryset_manager
    def area(self, *args, **kwargs):
        return self.get_query_set().area(*args, **kwargs)

    @queryset_manager
    def centroid(self, *args, **kwargs):
        return self.get_query_set().centroid(*args, **kwargs)

    @queryset_manager
    def collect(self, *args, **kwargs):
        return self.get_query_set().collect(*args, **kwargs)

    @queryset_manager
    def difference(self, *args, **kwargs):
        return self.get_query_set().difference(*args, **kwargs)

    @queryset_manager
    def distance(self, *args, **kwargs):
        return self.get_query_set().distance(*args, **kwargs)

    @queryset_manager
    def envelope(self, *args, **kwargs):
        return self.get_query_set().envelope(*args, **kwargs)

    @queryset_manager
    def extent(self, *args, **kwargs):
        return self.get_query_set().extent(*args, **kwargs)

    @queryset_manager
    def extent3d(self, *args, **kwargs):
        return self.get_query_set().extent3d(*args, **kwargs)

    @queryset_manager
    def force_rhr(self, *args, **kwargs):
        return self.get_query_set().force_rhr(*args, **kwargs)

    @queryset_manager
    def geohash(self, *args, **kwargs):
        return self.get_query_set().geohash(*args, **kwargs)

    @queryset_manager
    def geojson(self, *args, **kwargs):
        return self.get_query_set().geojson(*args, **kwargs)

    @queryset_manager
    def gml(self, *args, **kwargs):
        return self.get_query_set().gml(*args, **kwargs)

    @queryset_manager
    def intersection(self, *args, **kwargs):
        return self.get_query_set().intersection(*args, **kwargs)

    @queryset_manager
    def kml(self, *args, **kwargs):
        return self.get_query_set().kml(*args, **kwargs)

    @queryset_manager
    def length(self, *args, **kwargs):
        return self.get_query_set().length(*args, **kwargs)

    @queryset_manager
    def make_line(self, *args, **kwargs):
        return self.get_query_set().make_line(*args, **kwargs)

    @queryset_manager
    def mem_size(self, *args, **kwargs):
        return self.get_query_set().mem_size(*args, **kwargs)

    @queryset_manager
    def num_geom(self, *args, **kwargs):
        return self.get_query_set().num_geom(*args, **kwargs)

    @queryset_manager
    def num_points(self, *args, **kwargs):
        return self.get_query_set().num_points(*args, **kwargs)

    @queryset_manager
    def perimeter(self, *args, **kwargs):
        return self.get_query_set().perimeter(*args, **kwargs)

    @queryset_manager
    def point_on_surface(self, *args, **kwargs):
        return self.get_query_set().point_on_surface(*args, **kwargs)

    @queryset_manager
    def reverse_geom(self, *args, **kwargs):
        return self.get_query_set().reverse_geom(*args, **kwargs)

    @queryset_manager
    def scale(self, *args, **kwargs):
        return self.get_query_set().scale(*args, **kwargs)

    @queryset_manager
    def snap_to_grid(self, *args, **kwargs):
        return self.get_query_set().snap_to_grid(*args, **kwargs)

    @queryset_manager
    def svg(self, *args, **kwargs):
        return self.get_query_set().svg(*args, **kwargs)

    @queryset_manager
    def sym_difference(self, *args, **kwargs):
        return self.get_query_set().sym_difference(*args, **kwargs)

    @queryset_manager
    def transform(self, *args, **kwargs):
        return self.get_query_set().transform(*args, **kwargs)

    @queryset_manager
    def translate(self, *args, **kwargs):
        return self.get_query_set().translate(*args, **kwargs)

    @queryset_manager
    def union(self, *args, **kwargs):
        return self.get_query_set().union(*args, **kwargs)

    @queryset_manager
    def unionagg(self, *args, **kwargs):
        return self.get_query_set().unionagg(*args, **kwargs)


#class CityManager(GeoManager):
#	def nearest_to(self, lat, lon):
#		#Wrong x y order
#		#p = Point(float(lat), float(lon))
#		p = Point(float(lon), float(lat))
#		return self.nearest_to_point(p)
#
#	def nearest_to_point(self, point):
#		return self.distance(point).order_by('distance')[0]


class Country(Document, GeoManager):
    name = StringField(max_length = 200)
    code = StringField(max_length = 2)
    population = IntField()
    continent = StringField(max_length = 2)
    tld = StringField(max_length = 5, unique=True)

    meta = {
        'indexes': ['code'],
        'ordering': ['name'],
    }

    def __unicode__(self):
        return self.name

    @property
    def hierarchy(self):
        return [self]


class Region(Document, GeoManager):
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    code = StringField(max_length = 10)
    country = ReferenceField(Country)

    meta = {
        'indexes': ['slug', 'code'],
    }

    def __unicode__(self):
        return "%s, %s" % (self.name, self.country)

    @property
    def hierarchy(self):
        list = self.country.hierarchy
        list.append(self)
        return list


class City(Document, GeoManager):
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    region = ReferenceField(Region)
    location = GeoPointField()
    population = IntField()

    meta = {
        'indexes': ['slug'],
    }

    def __unicode__(self):
        return "%s, %s" % (self.name, self.region)

    @property
    def hierarchy(self):
        list = self.region.hierarchy
        list.append(self)
        return list


class District(Document, GeoManager):
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    city = ReferenceField(City)
    location = GeoPointField()
    population = IntField()

    meta = {
        'indexes': ['slug'],
    }

    def __unicode__(self):
        return u"%s, %s" % (self.name, self.city)

    @property
    def hierarchy(self):
        list = self.city.hierarchy
        list.append(self)
        return list
