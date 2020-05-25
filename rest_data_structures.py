#!/usr/bin/env python3

class Cars(object):
    def __init__(self, Make=None, Model=None, PrimaryDriver=None):
        self.Make = Make
        self.Model = Model
        self.Year = Year
        self.PrimaryDriver = PrimaryDriver

    def get_mapping(self):
        return {'Make': self.Make,
                'Model': self.Model,
                'Year': self.Year,
                'PrimaryDriver': self.PrimaryDriver}

    def validate(self, other):
        keys = {'Make', 'Model', 'Year', 'PrimaryDriver'}
        sother = set(other)
        return keys.issubset(other)
