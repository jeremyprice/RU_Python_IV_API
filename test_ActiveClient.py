#!/usr/bin/env python2

from client_lib import ActiveClient, InvalidClient, ClientManager
import unittest


class ClientManagerCase(unittest.TestCase):
    def test_create_ClientManager_instance(self):
        try:
            cm = ClientManager()  # noqa
        except NameError:
            self.fail("Can't create a ClientManager class")

    def test_new_client(self):
        cm = ClientManager()
        client = cm.new_client()
        self.assertIsInstance(client, ActiveClient)

    def test_get_client(self):
        cm = ClientManager()
        client = cm.new_client()
        client2 = cm.get_client(client.id)
        self.assertEquals(client, client2)

    def test_clean_list(self):
        import time
        cm = ClientManager()
        client = cm.new_client()
        old_timeout = ActiveClient.CLIENT_TIMEOUT
        ActiveClient.CLIENT_TIMEOUT = 1
        time.sleep(1.1)
        client = cm.get_client(client.id)
        ActiveClient.CLIENT_TIMEOUT = old_timeout
        self.assertIsNone(client)


class InvalidClientCase(unittest.TestCase):
    def test_create_InvalidClient_class(self):
        try:
            ac = InvalidClient('123')  # noqa
        except NameError:
            self.fail("Can't create an InvalidClient class")


class ActiveClientCase(unittest.TestCase):
    '''test all things to do with the ActiveClient class'''

    def test_create_ActiveClient_instance(self):
        try:
            ac = ActiveClient('123')  # noqa
        except NameError:
            self.fail("Can't create an ActiveClient class")

    def test_id_arg(self):
        ac_id = '123'
        ac = ActiveClient(ac_id)
        self.assertEquals(ac.id, ac_id)

    def test_creation_time(self):
        import datetime
        ac = ActiveClient('123')
        delta = datetime.datetime.now() - ac.creation_time
        self.assertLess(delta.seconds, 2)

    def test_first_path(self):
        ac = ActiveClient('123')
        self.assertEqual(len(ac.path_index), 1)

    def test_path_depth_not_found(self):
        ac = ActiveClient('123')
        self.assertEqual(ac.get_path_depth('not_in_there'), -1)

    def test_get_next_path_first(self):
        ac = ActiveClient('123')
        title, path = ac.get_next_path()
        self.assertEqual(path, ac.path_index[0])

    def test_get_next_path_ordering(self):
        ac = ActiveClient('123')
        title1, path1 = ac.get_next_path()
        title2, path2 = ac.get_next_path(path1)
        title1_again, path1_again = ac.get_next_path()
        self.assertEqual(path1, path1_again)
        self.assertNotEqual(path1, path2)

    def test_validate_path_exists(self):
        ac = ActiveClient('123')
        title, path = ac.get_next_path()
        self.assertTrue(ac.validate_path(path))

    def test_validate_path_not_exists(self):
        ac = ActiveClient('123')
        self.assertFalse(ac.validate_path('not_in_there'))

    def test_link_titles(self):
        ac = ActiveClient('123')
        paths = []
        next_path = ac.get_next_path()
        while next_path:
            title, path = next_path
            paths.append(title)
            next_path = ac.get_next_path(path)
        self.assertSetEqual(set(paths), set(ActiveClient.LINK_TITLES))

    def test_is_valid(self):
        ac = ActiveClient('123')
        self.assertTrue(ac.is_valid())

    def test_timeout(self):
        import time
        ac = ActiveClient('123')
        old_timeout = ActiveClient.CLIENT_TIMEOUT
        ActiveClient.CLIENT_TIMEOUT = 1
        time.sleep(1.1)
        self.assertFalse(ac.is_valid())
        with self.assertRaises(InvalidClient):
            ac.get_next_path()
        with self.assertRaises(InvalidClient):
            ac.get_path_depth('123')
        with self.assertRaises(InvalidClient):
            ac.validate_path('123')
        ActiveClient.CLIENT_TIMEOUT = old_timeout

if __name__ == '__main__':
    unittest.main()
