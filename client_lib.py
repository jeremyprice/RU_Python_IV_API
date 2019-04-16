import datetime
import random
from utils import generate_id
import redis


class InvalidClient(Exception):
    pass


class ActiveClient(object):

    CLIENT_TIMEOUT = 5  # seconds
    LINK_TITLES = ['first_link', 'next_url', 'url_no_2',
                   'almost_there', 'penultimate']
    EASY_LINK_TITLES = ['next'] * 10

    def __init__(self, my_id, easy=False):
        self.my_id = my_id
        self.path_map = {}
        self.path_index = [generate_id()]
        self.creation_time = datetime.datetime.now()
        if easy:
            self.my_titles = ActiveClient.EASY_LINK_TITLES[:]
        else:
            self.my_titles = ActiveClient.LINK_TITLES[:]
        random.shuffle(self.my_titles)

    @property
    def id(self):
        return self.my_id

    def get_next_path(self, from_path=None):
        if not self.is_valid():
            raise InvalidClient()
        if from_path is None:
            return (self.my_titles[0], self.path_index[0])
        if from_path in self.path_map:
            index = self.path_index.index(from_path)
            title = self.my_titles[index]
            return (title, self.path_map[from_path])
        if len(self.path_index) < len(self.my_titles):
            new_path = generate_id()
            self.path_map[from_path] = new_path
            self.path_index.append(new_path)
            index = len(self.path_index) - 1
            title = self.my_titles[index]
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


class RedisActiveClient(ActiveClient):
    def __init__(self, my_id, redis_i, easy=False, load=False):
        super(RedisActiveClient, self).__init__(my_id, easy=easy)
        self.redis = redis_i
        self.next_path_key = 'next_{}'.format(my_id)
        self.title_map_key = 'title_map_{}'.format(my_id)
        if load:
            self._load_from_redis()
        else:
            self._new_client()
            self._save_to_redis()

    def _new_client(self):
        paths, self.path_map = self._generate_all_paths()
        self.next_path_map = {paths[i]: paths[i+1] for i in range(len(paths)-1)}
        self.next_path_map['start'] = paths[0]

    def _load_from_redis(self):
        self.path_map = self.redis.hgetall(self.title_map_key)
        self.next_path_map = self.redis.hgetall(self.next_path_key)
        if not self.next_path_map:
            raise KeyError("Invalid client id")

    def _save_to_redis(self):
        pipe = self.redis.pipeline()
        [pipe.hset(self.next_path_key, k, v) for k, v in self.next_path_map.items()]
        [pipe.hset(self.title_map_key, k, v) for k, v in self.path_map.items()]
        # TODO: reenable these after testing
        pipe.expire(self.next_path_key, ActiveClient.CLIENT_TIMEOUT)
        pipe.expire(self.title_map_key, ActiveClient.CLIENT_TIMEOUT)
        pipe.execute()

    def _generate_all_paths(self):
        paths = [generate_id() for i in range(len(self.my_titles))]
        path_map = dict(zip(paths, self.my_titles))
        return (paths, path_map)

    def get_next_path(self, from_path=None):
        if from_path is None:
            from_path = 'start'
        next_path = self.redis.hget(self.next_path_key, from_path)
        if next_path is None:
            return None
        title = self.redis.hget(self.title_map_key, next_path).decode()
        return (title, next_path)

    def is_valid(self):
        return bool(self.redis.exists(self.next_path_key))


class ClientManager(object):
    def __init__(self):
        self.clients = {}

    def new_client(self, easy=False):
        '''Create a new client and add it to the managed list'''
        self._clean_list()
        cl_id = generate_id()
        nc = ActiveClient(cl_id, easy=easy)
        self.clients[cl_id] = nc
        return nc

    def get_client(self, client_id):
        '''Get a client from the store based on client_id
        returns valid ActiveClient object on success or None on error'''
        self._clean_list()
        try:
            client = self.clients[client_id]
        except KeyError:
            return None
        if client.is_valid():
            return client
        else:
            return None

    def _clean_list(self):
        self.clients = {k: v for k, v in self.clients.items() if v.is_valid()}


class RedisClientManager(ClientManager):
    def __init__(self):
        super(RedisClientManager, self).__init__()
        self.redis = redis.StrictRedis()  # defaults to localhost:6379

    def new_client(self, easy=False):
        return RedisActiveClient(generate_id(), self.redis, easy=easy)

    def get_client(self, client_id):
        try:
            nc = RedisActiveClient(client_id, self.redis, load=True)
        except KeyError:
            return None
        else:
            return nc
