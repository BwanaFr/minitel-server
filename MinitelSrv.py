'''
Created on 18 Oct 2019

@author: mdonze
'''
import logging
import os
import yaml
import logging.config

from minitel_server import constant
from minitel_server.tcp_server import TCPServer
from minitel_server.configuration import Configuration

logger = logging.getLogger('main')


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            #                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
    #                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        #        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


def main():
    setup_logging()
    Configuration.load_configuration()

    # Run the server
    ports = []
    for dirName in next(os.walk(Configuration.page_folder))[1]:
        logger.info("Searching service in " + dirName)
        try:
            ports.append(int(dirName))
        except:
            pass
    servers = []
    for p in ports:
        srv = TCPServer(p)
        srv.start()
        servers.append(srv)

    for s in servers:
        s.join()


if __name__ == '__main__':
    main()
