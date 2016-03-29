#!/usr/bin/env python2

from client_lib import ActiveClient, InvalidClient
import unittest


class ActiveClientCase(unittest.TestCase):
    '''test all things to do with the ActiveClient class'''

    def test_create_ActiveClient_class(self):
        try:
            ac = ActiveClient('123')  # noqa
        except NameError:
            self.fail("Can't create an ActiveClient class")

    def test_create_InvalidClient_class(self):
        try:
            ac = InvalidClient('123')  # noqa
        except NameError:
            self.fail("Can't create an InvalidClient class")

    # def test_id_arg(self):
    #    ac = ActiveClient('123')


if __name__ == '__main__':
    unittest.main()
