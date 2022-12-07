import sys
from client import HttpcClient
import argparse


class Httpc(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='An implementation of HTTP library',
            usage='''The requests are:
        get     executes a HTTP GET request and prints the response.
        post    executes a HTTP POST request and prints the response.
        help    prints this screen.
Use "httpc help [command]" for more information about a command.''')
        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)()

    def postMessage(self):
        print(
            'usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL'
            '\nPost executes a HTTP POST request for a given URL with inline data or from file.'
            '\n-v \t\t\tPrints the detail of the response such as udp, status, and headers.'
            '\n-h key:value \t\tAssociates headers to HTTP Request with the format key:value.'
            '\n-d string \t\tAssociates an inline data to the body HTTP POST request.'
            '\n-f file \t\tAssociates the content of a file to the body HTTP POST request.'
            '\n-o file \t\tOutputs POST response body to a provided file'
            '\n\nEither [-d] or [-f] can be used but not both.')

    def helpMessage(self):
        print('httpc is a curl-like application but supports HTTP udp only.'
              '\nUsage:'
              '\n\thttpc command [arguments]'
              '\nThe requests are:'
              '\n\tget \texecutes a HTTP GET request and prints the response.'
              '\n\tpost \texecutes a HTTP POST request and prints the response.'
              '\n\thelp \tprints this screen.'
              '\nUse "httpc help [command]" for more information about a command.')


    def getMessage(self):
        print(
            '\nusage: httpc get [-v] [-h key:value] URL'
            '\n\nGet executes a HTTP GET request for a given URL.'
            '\n-v \t\tPrints the detail of the response such as udp, status, and headers.'
            '\n-h key:value \tAssociates headers to HTTP Request with the format: key:value'
            '\n-o file \t\tOutputs GET response body to a provided file')

    def help(self):
        parser = argparse.ArgumentParser(description='Get information about httpc requests')
        parser.add_argument("request", nargs='?', help="Command to provide information about", default='help', choices=['help', 'get', 'post'])
        args = parser.parse_args(sys.argv[2:])
        if (args.request == 'help'):
           self.helpMessage()
        elif (args.request == 'get'):
            self.getMessage()
        elif (args.request == 'post'):
            self.postMessage()


    def post(self):
        parser = argparse.ArgumentParser(add_help=False,
            description='Parser for post requests')
        parser.add_argument("-v", "--verbose", help="verbose",  action="store_true")
        parser.add_argument("-h", "--header", help="HTTP headers in key:value format ", action='append', type=self.pair_checker)
        parser.add_argument("-d", "--data", help="Associate body of HTTP request with inline data", default=None)
        parser.add_argument("-f", "--file", help="Associate body of HTTP request with data from given file ", default=None)
        parser.add_argument("-o", "--writefile", help="write the body of the response to a file instead of the console ", default=None)
        parser.add_argument("URL", nargs='?', help="The url determining the targetted HTTP server")
        parser.add_argument("-rp","--routerPort", help="Port number of Router", default=3000, type=int)
        parser.add_argument("-rh","--routerHost", help="Host of router",default='localhost')
        args = parser.parse_args(sys.argv[2:])
        HttpcClient.execute_post_request(args)

    def get(self):
        parser = argparse.ArgumentParser(add_help=False,
            description='Parser for get requests')
        parser.add_argument("-v", "--verbose", help="verbose",  action="store_true")
        parser.add_argument("-h", "--header", help="HTTP headers in key:value format ", action='append', type=self.pair_checker)
        parser.add_argument("-o", "--writefile", help="write the body of the response to a file instead of the console ", default=None)
        parser.add_argument("URL", help="The url determining the targetted HTTP server")
        parser.add_argument("-rp","--routerPort", help="Port number of Router", default=3000, type=int)
        parser.add_argument("-rh","--routerHost",  help="Host of router",default='localhost')
        args = parser.parse_args(sys.argv[2:])

        HttpcClient.execute_get_request(args)




    def pair_checker(self, s):
        packet_pairing = s.split(":")
        packet_pairing = [x for x in packet_pairing if x != '']
        if (len(packet_pairing) != 2):
            message = "Please enter the key:value format!!!!!"
            raise argparse.ArgumentTypeError(message)
        return s




if __name__ == '__main__':
    Httpc()