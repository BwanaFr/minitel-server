'''
Created on 18 Oct 2019

@author: mdonze
'''
import logging
import os

from MinitelServer.server import MinitelServer 
from MinitelServer import constant

def main():
    
    logging.basicConfig(level=logging.INFO)
    # Run the server
    ports = []
    for dirName in next(os.walk(constant.PAGES_LOCATION))[1]:
        print("Searching service in " + dirName)        
        try:
            ports.append(int(dirName))
            print("Port " + dirName)
        except:
            pass
    
    MinitelServer(ports).run()
    #page = MinitelPage.getPage("root")
    #print('Page name ' + page.name)

if __name__ == '__main__':
    main()
