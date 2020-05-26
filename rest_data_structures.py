#!/usr/bin/env python3


class RDS(object):
    '''Base class for all REST Data Structures'''
    def __init__(self, *args, **kwargs):
        self.info = {k: v for k,v in kwargs.items() if k[0].isupper()}

        if 'other' in kwargs and kwargs['other']:
            self.update(other)

    def get_mapping(self):
        return self.info

    def validate(self, other):
        keys = set(self.info)
        sother = set(other)
        return keys.issubset(other)

    def create(self, other):
        if self.validate(other):
            for k in self.info:
                self.info[k] = other[k]
            return True
        else:
            return False

    def update(self, other):
        for k in other:
            if k in self.info:
                self.info[k] = other[k]


class Car(RDS):
    def __init__(self, Make=None, Model=None, PrimaryDriver=None, Name=None, Color=None,
                 Year=None, other=None):
        super(Car, self).__init__(Make=Make, Model=Model, PrimaryDriver=PrimaryDriver,
                                  Name=Name, Color=Color, Year=Year, other=other)

    def help(self):
        return {'Make': 'The make (manufacturer) of the car',
                'Model': 'The model of the car',
                'Year': 'The year the car was manufactured',
                'Name': 'The human-friendly name for this car',
                'Color': 'The color of the car',
                'PrimaryDriver': 'The name of the person who primarily drives this car'}

class Appliance(RDS):
    def __init__(self, Make=None, Model=None, Location=None, Color=None, Type=None,
                 Year=None, other=None):
        super(Car, self).__init__(Make=Make, Model=Model, Type=Type,
                                  Location=Location, Color=Color, Year=Year, other=other)

    def help(self):
        return {'Make': 'The make (manufacturer) of the appliance',
                'Model': 'The model of the appliance',
                'Year': 'The year the appliance was purchased',
                'Location': 'The location this appliance lives at',
                'Color': 'The color of the appliance',
                'Type': 'The type of the appliance (i.e. toaster, oven, fridge)'}


class Pantry(RDS):
    def __init__(self, Name=None, Quantity=None, Measure=None, ExpirationDate=None, other=None):
        super(Car, self).__init__(Name=Name, Quantity=Quantity, Measure=Measure,
                                  ExpirationDate=ExpirationDate, other=other)

    def help(self):
        return {'Name': 'The name of this item in the pantry',
                'Quantity': 'How many of these items are in the pantry',
                'Measure': 'How much of each item do you have (i.e. 1 lb, 12 oz)?',
                'ExpirationDate': 'The date this item will expire'}
