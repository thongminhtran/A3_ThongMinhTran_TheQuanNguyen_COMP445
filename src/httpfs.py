
import sys
from serverhelper import ServerHttp
import argparse


class httpfs(object):
    def __init__(self):
        parsing_context_value = argparse.ArgumentParser(
            description='HTTP server library')
        parsing_context_value.add_argument("-v", "--verbose", help="print debug messages",  action="store_true")
        parsing_context_value.add_argument("-p", "--port", help="Specifies the port number that the server will listen and serve at", default=8080, type=int)
        parsing_context_value.add_argument("-d", "--directory", help="Specifies the directory that the server will use to read/write quested files. Default is the current directory when launching the application", default='public')
        parsing_context_value.add_argument("-rp","--routerPort", help="Port number of Router", default=3000, type=int)
        parsing_context_value.add_argument("-rh","--routerHost", help="Host of router",default='localhost')
        string = parsing_context_value.parse_args(sys.argv[1:])
        database = ServerHttp(string.verbose, string.port, string.directory, string.routerPort, string.routerHost)
        database.initiate()
        if not hasattr(self, string.command):
            print ('Invalid input. Please check!!!!!')
            parsing_context_value.print_help()
            exit(1)
        getattr(self, string.command)()



if __name__ == '__main__':
    httpfs()