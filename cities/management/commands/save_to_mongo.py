'''
Created on 2011-07-31

@author: George
'''
from django.core.management.base import BaseCommand
import os
from django.core.management.commands.loaddata import Command as LoadCommand
import re
import sys
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
    
    def __init__(self, country_codes):
        self.country_codes = [country_code.upper()
                              for country_code in country_codes]
        self.fixtures_dir = '%s/../../fixtures' % os.path.dirname(__file__)
        self.src_data = simplejson.load(open('%s/geonames_dump.json'
                                             % self.fixtures_dir), 'cp1252')
        self.lonlat = re.compile('(?P<lon>-?\d+\.\d+) (?P<lat>-?\d+\.\d+)')

    def to_db(self):
        for model in self.src_data:
            model_class = self.MODELS[model['model']]
            new_instance = model_class(id=model['pk'])
            for field, value in model['fields'].iteritems():
                if field == 'location':
                    match = self.lonlat.search(value)
                    # TODO: verify lat/lon precision of fixtures and find a way
                    #       how to deal with them
                    value = ((float(match.group('lat')),
                              float(match.group('lon')))) 
                elif isinstance(getattr(model_class, field), ReferenceField):
                    reference_class = self.MODELS[field]
                    value = reference_class.objects.get(id=value)
                setattr(new_instance, field, value)
            print "Saving %s %s" % (model_class.__name__, new_instance)
            new_instance.save()


class Command(BaseCommand):

    help = 'Import selected countries into database.'
    args = "code [code ...]"
    option_list = LoadCommand.option_list
    
    def handle(self, *args, **options):
#        if not len(args):
#            self.stderr.write('No countries specified. Task is aborted.')
#            sys.exit()
        extracter = Extracter(args)
        extracter.to_db()
