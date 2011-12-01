from math import radians, sin, cos, asin, sqrt

from mongoengine import *


class Country(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length = 200)
    code = StringField(max_length = 2, unique=True)
    population = IntField()
    continent = StringField(max_length = 2)
    tld = StringField(max_length = 5, unique=True)

    meta = {
        'indexes': ['code'],
        'ordering': ['name'],
    }

    def __repr__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return self.name

    @property
    def hierarchy(self):
        return [self]


class Region(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    code = StringField(max_length = 10)
    country = ReferenceField(Country)

    meta = {
        'indexes': ['slug', 'code'],
    }

    def __repr__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return "%s, %s" % (self.name, self.country)

    @property
    def hierarchy(self):
        list = self.country.hierarchy
        list.append(self)
        return list


class GeoMixin(object):

    """
    Some custom query methods on top of the ones implemented in mongoengine

    NOTE the order ((latitude, longitude))!
    """

    @classmethod
    def nearest(cls, location):
        longitute, latitude = location
        return cls.near(lon, lat).first()

    @classmethod
    def near(cls, location):
        """
        location == (( longitude, latitude ))
        """
        return cls.objects.filter(location__near_sphere=location)

    def distance_to(self, other):
        """
        Using the haversine formula. Mongo-db should do that already -
        How to query using mongo-dbs powers??
        """
        if isinstance(other, (tuple, list)):
            lon, lat = other
        else: # if !tuple we expect an object with a geopoint field 'location'
            lon, lat = other.location[0], other.location[1]
        diff_lon = radians(self.location[0] - lon)
        diff_lat = radians(self.location[1] - lat)
        lat1, lat2 = radians(self.location[1]), radians(lat)

        haversine_lat = sin(diff_lat / 2.0) ** 2
        haversine_lon = sin(diff_lon / 2.0) ** 2
        a = haversine_lat + cos(lat1) * cos(lat2) * haversine_lon

        great_circle_distance = 2 * asin(min(1,sqrt(a)))

        earth_radius = 6378 # in km
        distance = earth_radius * great_circle_distance

        return distance


class City(Document, GeoMixin):
    id = IntField(primary_key=True)
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    region = ReferenceField(Region)
    country = ReferenceField(Country) # added for country rel. search
    location = GeoPointField()
    population = IntField()

    meta = {
        'indexes': ['slug'],
    }

    def __repr__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return "%s, %s, %s" % (self.name, self.region.name,
                               self.region.country.name)

    @property
    def hierarchy(self):
        list = self.region.hierarchy
        list.append(self)
        return list

    def save(self, *args, **kwargs):
        self.country = self.country or self.region.country
        super(City, self).save(*args, **kwargs)

class District(Document, GeoMixin):
    id = IntField(primary_key=True)
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
