from mongoengine import *


class Country(Document):
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


class Region(Document):
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


class GeoDocument(Document):

    @classmethod
    def nearest_to(cls, lat, lon):
        return cls.object.filter(location__near=[lon, lat])


class City(GeoDocument):
    name = StringField(max_length = 200)
    slug = StringField(max_length = 200)
    region = ReferenceField(Region)
    country = ReferenceField(Country) # added for country rel. search
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

    def save(self, *args, **kwargs):
        self.country = self.country or self.region.country
        super(City, self).save(*args, **kwargs)

class District(GeoDocument):
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
