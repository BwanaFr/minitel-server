'''
Created on 18 Oct 2019

@author: mdonze
'''
import logging

from MinitelServer.server import MinitelServer 
from MinitelServer.page import MinitelPage

def main():
    
    logging.basicConfig(level=logging.INFO)
    # Run the server
    MinitelServer(3615).run()
    #page = MinitelPage.getPage("root")
    #print('Page name ' + page.name)

if __name__ == '__main__':
    main()
