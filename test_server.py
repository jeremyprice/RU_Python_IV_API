#!/usr/bin/env python2

import server
import unittest
import uuid
import json
import validators


class ServerTestCase(unittest.TestCase):
    '''test the actual server interaction'''
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def _json_get(self, url):
        result = self.app.get(url)
        # let the next line blow up if JSON error
        return json.loads(result.data)

    def _json_post(self, url, data):
        json_d = json.dumps(data)
        result = self.app.post(url, data=json_d,
                               content_type="application/json")
        # let the next line blow up if JSON error
        return json.loads(result.data)

    def test_get_root_json_len(self):
        rootj = self._json_get('/')
        self.assertEqual(len(rootj), 2)

    def test_get_root_json_has_token(self):
        rootj = self._json_get('/')
        self.assertIn('token', rootj)

    def test_get_root_json_valid_token(self):
        rootj = self._json_get('/')
        try:
            uid = uuid.UUID(rootj['token'])  # noqa
        except ValueError:
            self.fail("Invalid id for token")

    def test_first_url(self):
        rootj = self._json_get('/')
        rootj.pop('token')
        key, url = rootj.popitem()
        self.assertTrue(validators.url(url, require_tld=False))

    def test_post_2nd_step(self):
        rootj = self._json_get('/')
        token = rootj.pop('token')
        key, url = rootj.popitem()
        secondj = self._json_post(url, data={'token': token})
        self.assertIn('token', secondj)
        secondj.pop('token')
        key, url = secondj.popitem()
        self.assertTrue(validators.url(url, require_tld=False))

    def test_all_steps(self):
        rootj = self._json_get('/')
        token = rootj.pop('token')
        key, url = rootj.popitem()
        while url:
            nextj = self._json_post(url, data={'token': token})
            if 'answer' in nextj:  # we found the last item
                break
            self.assertIn('token', nextj)
            nextj.pop('token')
            key, url = nextj.popitem()
            self.assertTrue(validators.url(url, require_tld=False))

if __name__ == '__main__':
    unittest.main()
