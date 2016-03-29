#!/usr/bin/env python2

import server
import unittest
import uuid


class ServerHelpersTestCase(unittest.TestCase):
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def test_uniq_generate_id(self):
        id1 = server.generate_id()
        id2 = server.generate_id()
        self.assertNotEqual(id1, id2)

    def test_uuid_generate_id(self):
        id1 = server.generate_id()
        try:
            uid = uuid.UUID(id1)  # noqa
        except ValueError:
            self.fail("Invalid uuid from generate_id")

    def test_create_ActiveClient_class(self):
        try:
            ac = server.ActiveClient('123')  # noqa
        except NameError:
            self.fail("Can't create an ActiveClient class")

    def test_create_InvalidClient_class(self):
        try:
            ac = server.InvalidClient('123')  # noqa
        except NameError:
            self.fail("Can't create an InvalidClient class")


if __name__ == '__main__':
    unittest.main()
