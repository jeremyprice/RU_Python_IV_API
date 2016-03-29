import datetime
from utils import generate_id


class InvalidClient(Exception):
    pass


class ActiveClient(object):

    CLIENT_TIMEOUT = 60  # seconds
    LINK_TITLES = ['first_link', 'next_url', 'url_no_2',
                   'almost_there', 'penultimate']

    def __init__(self, my_id):
        self.my_id = my_id
        self.path_map = {}
        self.path_index = [generate_id()]
        self.creation_time = datetime.datetime.now()

    @property
    def id(self):
        return self.my_id

    def get_next_path(self, from_path=None):
        if not self.is_valid():
            raise InvalidClient()
        if from_path is None:
            return (ActiveClient.LINK_TITLES[0], self.path_index[0])
        if from_path in self.path_map:
            index = self.path_index.index(from_path)
            title = ActiveClient.LINK_TITLES[index]
            return (title, self.path_map[from_path])
        if len(self.path_index) < len(ActiveClient.LINK_TITLES):
            new_path = generate_id()
            self.path_map[from_path] = new_path
            self.path_index.append(new_path)
            index = len(self.path_index) - 1
            title = ActiveClient.LINK_TITLES[index]
            return (title, new_path)
        # if we get here we have exhausted all the links
        return None

    def get_path_depth(self, path):
        if not self.is_valid():
            raise InvalidClient()
        try:
            retval = self.path_index.index(path)
        except ValueError:
            retval = -1
        return retval

    def validate_path(self, path):
        if not self.is_valid():
            raise InvalidClient()
        return path in self.path_index

    def is_valid(self):
        delta = datetime.datetime.now() - self.creation_time
        return delta.seconds < ActiveClient.CLIENT_TIMEOUT


class ClientList(object):
    def __init__(self):
        self.clients = {}
