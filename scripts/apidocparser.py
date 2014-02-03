from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
from errno import EEXIST
from hashlib import md5
from json import dumps
from os import makedirs, path
from time import sleep, time
from urllib2 import urlopen

class APIDocParser(object):
    '''
    Parses the Stack Exchange API documentation
    '''
    
    _BASE_URL = 'http://api.stackexchange.com'
    
    def __init__(self, args):
        '''
        Initializes the parser
        '''
        self._args         = args
        self._last_request = 0
        self._map          = {
            'version':   self._args.version,
            'generated': datetime.now().isoformat(' '),
            'methods':   {
                'network': [],
                'site':    [],
            },
        }
    
    def _create_cache_dir(self):
        '''
        Creates the cache directory
        '''
        try:
            makedirs(self._args.cache_dir)
        except OSError as e:
            if not e.errno == EEXIST:
                raise
    
    def _load_page(self, path):
        '''
        Loads the specified page either directly or from the cache
        '''
        key      = md5(path).hexdigest()
        filename = path.join([self._args.cache_dir, key,])
        if self._args.use_cache:
            try:
                with open(filename, 'r') as file:
                    return BeautifulSoup(file.read(), 'html5lib')
            except IOError:
                pass
        sleep(max(1 - (time() - self._last_request), 0))
        print 'Retrieving %s...' % path
        content = urlopen(self._BASE_URL + path).read()
        self._last_request = time()
        if self._args.use_cache:
            with open(filename, 'w') as file:
                file.write(content)
        return BeautifulSoup(content, 'html5lib')
    
    def _parse(self):
        '''
        Retrieves documentation pages and parses them
        '''
        root = self._load_page('/docs')
        for div in root.find_all('div', 'method-name'):
            self._parse_method(div.a)
    
    def _parse_method(self, method):
        '''
        Parses the specified method
        '''
        page = self._load_page(method['href'])
        self._map['methods']['network'].append({
            'name': method.string,
        })
    
    def _write_map(self):
        '''
        Writes the generated map to file
        '''
        filename = path.join(self._args.output_dir, 'map.json')
        with open(filename, 'w') as file:
            file.write(dumps(self._map, indent=4 if self._args.prettyprint else None))
    
    def run(self):
        '''
        Begins parsing the API docs
        '''
        if self._args.use_cache:
            self._create_cache_dir()
        self._parse()
        self._write_map()

if __name__ == '__main__':
    parser = ArgumentParser(description='Parses the documentation for the Stack Exchange API')
    parser.add_argument('--use-cache',
                        action='store_true',
                        help='use a local cache to store content')
    parser.add_argument('--cache-dir',
                        metavar='DIRECTORY',
                        type=str,
                        default='cache',
                        help='directory to store cached content')
    parser.add_argument('--output-dir',
                        metavar='DIRECTORY',
                        type=str,
                        default='.',
                        help='directory to store generated map')
    parser.add_argument('--prettyprint',
                        action='store_true',
                        help='indent the generated JSON')
    parser.add_argument('--version',
                        metavar='VERSION',
                        type=str,
                        required=True,
                        help='API version used in generated map')
    APIDocParser(parser.parse_args()).run()