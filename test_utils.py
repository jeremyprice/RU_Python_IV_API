#!/usr/bin/env python2

import unittest
import uuid
import utils


class ServerHelpersTestCase(unittest.TestCase):
    '''test the simple existence of objects and helper functions'''

    def test_uniq_generate_id(self):
        id1 = utils.generate_id()
        id2 = utils.generate_id()
        self.assertNotEqual(id1, id2)

    def test_uuid_generate_id(self):
        id1 = utils.generate_id()
        try:
            uid = uuid.UUID(id1)  # noqa
        except ValueError:
            self.fail("Invalid uuid from generate_id")


if __name__ == '__main__':
    unittest.main()
