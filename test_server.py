#!/usr/bin/env python2

import server
import unittest
import uuid


class ServerHelpersTestCase(unittest.TestCase):
    '''test the simple existence of objects and helper functions'''

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


class ServerTestCase(unittest.TestCase):
    '''test the actual server interaction'''
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()


if __name__ == '__main__':
    unittest.main()
