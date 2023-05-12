import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'ii9gyhbmo2i3flo'
app_secret = 'xrtgmxy1m4m9t8v'
server_addr = "localhost"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('localhost', 8090))
        server_socket.listen(1)
        print('Socket listening on port 8090')

        print('Waiting for client request')
        # In the following line the program stops until the server receives 302 requests.
        client_connection, client_adress = server_socket.accept()

        # Receive 302 response from the explorer
        request = client_connection.recv(1024).decode()
        # print('\n' + request)

        # Search for the auth_code on the request
        first_line = request.split('\n')[0]
        aux_auth_code = first_line.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("Auth_code: " + auth_code)

        # Send a response to the user
        http_response = """\
            HTTP/1.1 200 OK

            <html>
            <head><title>Proba</title></head>
            <body>
            The authentication flow has completed. Close this window.
            </body>
            </html>
            """

        client_connection.sendall(str.encode(http_response))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        # Authorization
        uri = "https://www.dropbox.com/oauth2/authorize"
        data = {'client_id': app_key,
                'redirect_uri': redirect_uri,  # LoopBack IP address
                'response_type': 'code'}

        coded_data = urllib.parse.urlencode(data)
        uri = uri + '?' + coded_data
        webbrowser.open_new(uri)  # Open the request on the explorer (GET is the predetermined method)
        auth_code = self.local_server()

        # Exchange authorization code for access token
        uri = "https://api.dropboxapi.com/oauth2/token"
        headers = {'Host': 'api.dropboxapi.com',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'code': auth_code,
                'client_id': app_key,
                'client_secret': app_secret,
                'redirect_uri': redirect_uri,  # LoopBack IP address
                'grant_type': 'authorization_code'}

        response = requests.post(uri, headers=headers, data=data, allow_redirects=False)

        status_code = response.status_code
        content = response.text
        content_json = json.loads(content)
        access_token = content_json['access_token']
        print('Access token:' + access_token)

        self._access_token = access_token
        self._root.destroy()

    def list_folder(self, msg_listbox, cursor="", content_json_entries=[]):
        if not cursor:
            print("/list_folder")
            uri = "https://api.dropboxapi.com/2/files/list_folder"
            data = {'path': self._path}

        else:
            uri = "https://api.dropboxapi.com/2/files/list_folder/continue"
            data = {'cursor': cursor}

        data_json = json.dumps(data)
        # Call Dropbox API
        headers = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json',
                     'Content-Length': str(len(data_json))}
        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        content = response.text
        content_json = json.loads(content)
        if content_json['has_more']:
            self.list_folder(msg_listbox, content_json['cursor'], content_json_entries)
        else:
            self._files = helper.update_listbox2(msg_listbox, self._path, content_json_entries)

    def transfer_file(self, file_path, file_data):
        print("/upload " + file_path)


    def delete_file(self, file_path):
        print("/delete_file " + file_path)


    def create_folder(self, path):
        print("/create_folder " + path)

