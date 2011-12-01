import os
import re
import sys

from django.core.management.base import BaseCommand
from django.core.management.commands.loaddata import Command as LoadCommand
from django.utils import simplejson

from mongoengine import *
from mongoengine.queryset import OperationError
from mongoengine.base import ValidationError

from cities.models import *


class Extracter(object):

    MODELS = {
        'cities.country': Country,
        'country': Country,
        'cities.region': Region,
        'region': Region,
        'cities.city': City,
        'city': City,
        'cities.district': District,
        'district': District,
    }

    def __init__(self, country_codes=None, verbosity=None, fixtures_path=None):
        self.countries = ([code.upper() for code in country_codes]
                          if country_codes else (()))
        if not fixtures_path:
            fixtures_dir = '%s/../../fixtures' % os.path.dirname(__file__)
            fixtures_path = '%s/geonames_dump.json' % fixtures_dir
        self.src_data = simplejson.load(open(fixtures_path), 'cp1252')
        # decimal degrees in (longitude, latitude) order - same as for GeoJSON
        # --> http://geojson.org/geojson-spec.html
        self.lonlat = re.compile('(?P<lon>-?\d+\.\d+) (?P<lat>-?\d+\.\d+)')
        self.imported_countries, self.imported_country_ids = [], []
        self.imported_city_ids = []
        self.verbosity = int(verbosity) if verbosity else 0
        self.old_model_class = None

    def to_db(self):
        for model in self.src_data:
            pk, model_class = model['pk'], self.MODELS[model['model']]
            if self.verbosity >= 1 and model_class != self.old_model_class:
                print 'starting to import %s' % model_class
            self.old_model_class = model_class
            if not self.country_in_wishlist(model):
                if self.verbosity >= 2:
                    print 'skipping %s %s' % (model_class.__name__,
                                              model['fields']['name'])
                continue
            new_instance = model_class(id=pk)
            skip = False
            for field, value in model['fields'].iteritems():
                if field == 'location':
                    match = self.lonlat.search(value)
                    # preserving ((lon, lat)) order
                    value = ((
                        float(match.group('lon')),
                        float(match.group('lat')),
                    ))
                elif isinstance(getattr(model_class, field), ReferenceField):
                    reference_class = self.MODELS[field]
                    try:
                        value = reference_class.objects.get(id=value)
                    except reference_class.DoesNotExist, e:
                        print ("%s with id %s not found - "
                               "skipping creation of %s %s"
                               % (reference_class, model['fields'][field],
                                  model_class, model['fields']['name']))
                        skip = True
                        break
                setattr(new_instance, field, value)
            if skip:
                continue
            new_instance.save()
            print "Saved %s %s" % (model_class.__name__, new_instance)
            if model_class == Country:
                self.imported_countries.append(new_instance)
                self.imported_country_ids.append(pk)
            elif model_class == City:
                self.imported_city_ids.append(model)

    def country_in_wishlist(self, model):
        model_class, code = model['model'], model['fields'].get('code')
        countries = self.imported_countries # these are Country instances
        if self.countries:
            if model_class == 'cities.country':
                if code not in self.countries:
                    return False
            elif model_class == 'cities.region':
                country = model['fields']['country'] # this is a pk
                if country not in self.imported_country_ids:
                    return False
            elif model_class == 'cities.city':
                region = Region.objects(id=model['fields']['region'])
                if not region or region[0].country not in countries:
                    return False
            else:
                assert model_class == 'cities.district'
                city = model['fields'].get('city') # this is a pk
                if city and not city in self.imported_city_ids:
                    return False
        # if not self.countries, all are in wishlist
        return True


class Command(BaseCommand):

    help = 'Import selected countries into database.'
    args = "code [code ...]"
    option_list = LoadCommand.option_list

    def handle(self, *args, **options):
        if not len(args):
            self.stderr.write('No countries specified. This will import all fixtures.')
            ans = raw_input("Continue Y/N: ")
            if ans.lower() not in ["y", "yes"]:
                sys.exit()
        country_codes = args[0].split(',') if args else None
        extracter = Extracter(country_codes, verbosity=options['verbosity'])
        extracter.to_db()
