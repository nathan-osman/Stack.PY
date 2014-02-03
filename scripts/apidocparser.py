from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
from errno import EEXIST
from hashlib import md5
from json import dumps, loads
from os import makedirs, path
from re import compile
from time import sleep, time
from urllib2 import urlopen

class APIDocParser(object):
    '''
    Parses the Stack Exchange API documentation
    '''
    
    _BASE_URL     = 'http://api.stackexchange.com'
    _PARAMETER_JS = compile(r'var\s+parameters\s*=\s*({.*});')
    
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
    
    def _fetch_page(self, page):
        '''
        Fetches the specified page either directly or from the cache
        '''
        key      = md5(page).hexdigest()
        filename = path.join(self._args.cache_dir, key)
        if not self._args.bypass_cache:
            try:
                with open(filename, 'r') as file:
                    return BeautifulSoup(file.read(), self._args.parser)
            except IOError:
                pass
        sleep(max(1 - (time() - self._last_request), 0))
        print 'Retrieving %s...' % page
        content = urlopen(self._BASE_URL + page).read()
        self._last_request = time()
        if not self._args.bypass_cache:
            with open(filename, 'w') as file:
                file.write(content)
        return BeautifulSoup(content, self._args.parser)
    
    def _parse_method(self, a):
        '''
        Parses the specified method
        '''
        page   = self._fetch_page(a['href'])
        script = page('script', text=self._PARAMETER_JS)
        self._map['methods']['network'].append({
            'name':       method.string,
            'parameters': self._parse_parameters(script),
        })
    
    def _parse_methods(self):
        '''
        Retrieves documentation pages and parses them
        '''
        root = self._fetch_page('/docs')
        for div in root.find_all('div', 'method-name'):
            self._parse_method(div.a)
    
    def _parse_parameters(self, script):
        if not len(script):
            return
        match = self._PARAMETER_JS.search(script[0].string)
        if match:
            return loads(match.group(1))
    
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
        if not self._args.bypass_cache:
            self._create_cache_dir()
        self._parse_methods()
        self._write_map()

if __name__ == '__main__':
    parser = ArgumentParser(description='Parses the documentation for the Stack Exchange API')
    parser.add_argument('--bypass-cache',
                        action='store_true',
                        help='do not use a local cache to store content')
    parser.add_argument('--cache-dir',
                        metavar='DIRECTORY',
                        type=str,
                        default='cache',
                        help='directory to store cached content')
    parser.add_argument('--version',
                        metavar='VERSION',
                        type=str,
                        required=True,
                        help='API version used in generated map')
    parser.add_argument('--parser',
                        metavar='PARSER',
                        choices=['lxml', 'html5lib',],
                        required=True,
                        help='parser for BeautifulSoup to use')
    parser.add_argument('--output-dir',
                        metavar='DIRECTORY',
                        type=str,
                        default='.',
                        help='directory to store generated map')
    parser.add_argument('--prettyprint',
                        action='store_true',
                        help='indent the generated JSON')
    APIDocParser(parser.parse_args()).run()