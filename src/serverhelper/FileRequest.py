from filemanager import FileManager
from urllib.parse import urlsplit
import json

REQUEST_QUERY = 1
class FileRequest:
    def __init__(self, request_params, directory, request_body):
        self.file_manager = FileManager(directory)
        self.request_params = request_params
        self.request_body = request_body
    
    def get_query(self):
        params = self.request_params
        query_awaiting = params[REQUEST_QUERY]
        if (query_awaiting == '/'):
            accepted_file_types = self.response_value('Accept')
            accepted_file_types = ['json','xml','txt', 'html'] if accepted_file_types == '*/*' else [accepted_file_types]
            return self.file_manager.get_all_files_in_dir(accepted_file_types)    
        elif ('?' in query_awaiting):
            argument_list = urlsplit(query_awaiting).query.split('&')
            arg_dict = {}
            for arg in argument_list:
                arg_key = arg[:arg.index('=')]
                arg_value = arg[arg.index('=') + 1:]
                arg_dict[arg_key] = arg_value
            return {
                'content': json.dumps({'args': arg_dict}),
                'status': 200,
                'mimetype': 'application/json'
            }
        else:
            file_path = query_awaiting[1:]
            return self.file_manager.get_file_content(file_path)
        
    def post_query(self):
        params = self.request_params
        query_awaiting = params[REQUEST_QUERY]
        if ('post' in query_awaiting):
            if ('?' in query_awaiting):\
            argument_list = urlsplit(query_awaiting).query.split('&')
            arg_dict = {}
            for arg in argument_list:
                arg_key = arg[:arg.index('=')]
                arg_value = arg[arg.index('=') + 1:]
                arg_dict[arg_key] = arg_value
            return {
                'content': json.dumps({"data": self.request_body, "args": arg_dict}),
                'status': 200,
                'mimetype': 'application/json'
            }
        else:
            dir_file = params[REQUEST_QUERY][1:]
            new_file = False if self.response_value('Overwrite').lower() == 'false' else True
            return self.file_manager.post_file_content(dir_file, self.request_body, new_file)
        
    def response_value(self, HEADER):
        header_value = HEADER + ":"
        if (header_value in self.request_params):
            return self.request_params[self.request_params.index(header_value) + 1]
        return ""