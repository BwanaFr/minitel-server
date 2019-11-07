'''
Created on 18 Oct 2019

@author: mdonze
'''
import logging
import os
import yaml
import logging.config

from MinitelServer.server import MinitelServer 
from MinitelServer import constant

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
    # Run the server
    ports = []
    for dirName in next(os.walk(constant.PAGES_LOCATION))[1]:
        logger.info("Searching service in " + dirName)        
        try:
            ports.append(int(dirName))
        except:
            pass
    
    MinitelServer(ports).run()
    #page = MinitelPage.getPage("root")
    #print('Page name ' + page.name)

if __name__ == '__main__':
    main()
