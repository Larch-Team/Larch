from genericpath import isfile
import os
import sys
from typing import Callable, Iterator, Union
from urllib import request as web_request
from urllib.error import URLError
from misc import setup_iter
from required_files import NEED
from json import loads
from tqdm import tqdm
from time import sleep


def try_gen(func: Callable[..., Union[str, None]]) -> Iterator[str]:
    def wrapped(*args, **kwargs):
        tries = 0
        while (info := func(*args, **kwargs)):
            tries += 1
            yield f'{info}, retrying in 5 seconds (retried {tries} time(s))'
            sleep(5)
        if tries > 0:
            yield 'It was successful'
    return wrapped


class FileManager(object):

    BRANCH = "dist-lab"
    REPO_URL = f"https://raw.githubusercontent.com/Larch-Team/larch-plugins/{BRANCH}"
    _directory = None

    @property
    def directory(self):
        return type(self)._directory

    @directory.setter
    def directory(self, val):
        type(self)._directory = val

    _plugins = None

    @property
    def plugins(self):
        return type(self)._plugins

    @plugins.setter
    def plugins(self, val):
        type(self)._plugins = val

    _setups = None

    @property
    def setups(self):
        return type(self)._setups

    @setups.setter
    def setups(self, val):
        type(self)._setups = val

    @try_gen
    def get_files(self) -> Union[None, str]:
        if self.plugins is None or self.setups is None:
            try:
                response = web_request.urlopen(f"{self.REPO_URL}/files.json")
            except URLError as e:
                return f'Couldn\'t download the file list'
            files = loads(response.read())
            self.plugins = files['plugins']
            self.setups = files['setups']
        return None

    def __init__(self, debug: bool = None, larch_version: str = None) -> None:
        super().__init__()
        assert self.directory or (
            debug is not None and larch_version is not None), "Jedno trzeba dostarczyć"
        if larch_version is not None and debug is not None:
            self.debug = debug
            self.select_dir(larch_version)

    def select_dir(self, larch_version: str):
        # MANIFEST = {
        #     'larch_version':larch_version,
        #     'additional':[]
        # }

        if self.debug:
            self.directory = os.path.abspath(
                __file__).removesuffix('manager.py')+'../appdata'
        else:
            self.directory = os.getenv('appdata')+'/Larch'
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)

        # if not os.path.isfile(f'{self.directory}/manifest.json'):
        #     with open(f'{self.directory}/manifest.json', 'w') as f:
        #         dump(MANIFEST, f)

        os.chdir(self.directory)
        sys.path = [self.directory] + sys.path

    def prepare_dirs(self, folder: str):
        path = self.directory[:]
        for i in folder.split('/'):
            path = path + '/' + i
            if '.' in i:
                break
            if not os.path.isdir(path):
                os.mkdir(path)

    @try_gen
    def download_file(self, file: str, required: bool = False) -> Union[None, str]:
        self.prepare_dirs(file)
        url = f"{self.REPO_URL}/{file}"
        try:
            response = web_request.urlopen(url)
        except URLError as e:
            return f'Couldn\'t download {file}'
        webContent = response.read()
        with open(f'{self.directory}/{file}', 'wb') as f:
            f.write(webContent)
            # if not required:
            #     man = self.read_manifest()
            #     if file not in man['additional']:
            #         man['additional'].append(file)
            #         self.write_manifest(man)
        return None

    def download_required(self):
        desc = 'Please wait while we download required plugins'
        pbar = tqdm(NEED, desc, unit='file(s)', position=0, leave=True)
        for i in pbar:
            pbar.write(f"Downloading {i}")
            if not isfile(f'{self.directory}/{i}'):
                for error in self.try_download(i, required=True):
                    pbar.write(error)
        os.system('self')

    def download_plugin(self, socket: str, plugin: str) -> Iterator[str]:
        yield "Checking the required files"
        yield from (f"\t{i}" for i in self.get_files())
        try:
            files = self.plugins.get(socket, None)[plugin]
        except TypeError:
            yield "No such socket"
            return
        except KeyError:
            yield "No such plugin"
            return
        for n, file in enumerate(files):
            yield f"({n+1}/{len(files)}) Downloading {file}"
            if isfile(f'{self.directory}/{file}'):
                yield "\tThis file already exists"
            else:
                yield from (f"\t{i}" for i in self.download_file(file))

    @staticmethod
    def setup_list() -> list[str]:
        return [name.removesuffix('.json') for name in os.listdir('setups')]

    def download_setup(self, setup_name: str) -> Iterator[str]:
        if setup_name in self.setup_list():
            yield "This setup exists locally"
            return
        yield "Checking if the setup exists"
        yield from (f"\t{i}" for i in self.get_files())
        try:
            file = self.setups[setup_name]
        except KeyError:
            yield "No such setup exists"
            return
        else:
            yield "\tSetup was found"
        yield f"Downloading {file}"
        yield from (f"\t{i}" for i in self.download_file(file))

    def download_setup_plugins(self, setup_name: str) -> Iterator[str]:
        SOCKET_AMOUNT = 5
        
        yield from self.download_setup(setup_name)
        if setup_name in self.setup_list():
            file = f'setups/{setup_name}.json'
        else:
            file = self.setups[setup_name]
        for n, (socket, plugin) in enumerate(setup_iter(file)):
            yield f"({n+1}/{SOCKET_AMOUNT}) Downloading {plugin} for the {socket} socket"
            yield from (f"\t{i}" for i in self.download_plugin(socket, plugin))

    # @staticmethod
    # def read_manifest():
    #     with open("manifest.json", 'r') as target:
    #         return load(target)

    # @staticmethod
    # def write_manifest(manifest):
    #     with open("manifest.json", 'w') as target:
    #         dump(manifest, target)
