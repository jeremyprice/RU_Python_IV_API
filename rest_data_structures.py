#!/usr/bin/env python3

class Car(object):
    def __init__(self, Make=None, Model=None, PrimaryDriver=None, Name=None, Color=None, Year=None):
        self.info = {'Make': Make,
                     'Model': Model,
                     'Year': Year,
                     'Color': Color,
                     'PrimaryDriver': PrimaryDriver,
                     'Name': Name}

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
