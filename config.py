from configparser import ConfigParser

import utilities

config_path = utilities.search_for_config()

config_parser = ConfigParser()
config_parser.read(config_path)

ssh_binary = config_parser.get('BINARIES', 'ssh')
dynamite_remote_root = config_parser.get('DIRECTORIES', 'dynamite_remote_root')