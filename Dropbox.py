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
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"

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
        print(status_code)
        content = response.text
        content_json = json.loads(content)
        access_token = content_json['access_token']
        print('Access token:' + access_token)
        print("Autentifikazio fluxua amaitu da.")

        self._access_token = access_token
        self._root.destroy()

    def list_folder(self, msg_listbox, cursor="", content_json_entries=[]):

        if self._path == '/':
            self._path = ''

        if not cursor:
            print("/list_folder")
            uri = "https://api.dropboxapi.com/2/files/list_folder"
            data = {'path': self._path, 'recursive': False}

        else:
            uri = "https://api.dropboxapi.com/2/files/list_folder/continue"
            data = {'cursor': cursor}

        data_json = json.dumps(data)

        # Call Dropbox API
        headers = {'Host': 'api.dropboxapi.com',
                   'Authorization': 'Bearer ' + self._access_token,
                   'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        content = response.content
        content_json = json.loads(content)

        content_json_entries = content_json['entries']

        if content_json['has_more']:
            self.list_folder(msg_listbox, content_json['cursor'], content_json_entries)
        else:
            self._files = helper.update_listbox2(msg_listbox, self._path, content_json_entries)

    def transfer_file(self, file_path, file_data):

        print("/upload " + file_path)

        uri = 'https://content.dropboxapi.com/2/files/upload'

        data = {"autorename": True,
                    "mode": "add",
                    "mute": False,
                    "path": file_path,
                    "strict_conflict": False}

        data_json = json.dumps(data)

        headers = {'Host': 'content.dropboxapi.com',
                        'Authorization': 'Bearer ' + self._access_token,
                        'Dropbox-API-Arg': data_json,
                        'Content-Type': 'application/octet-stream'}

        response = requests.post(uri, headers=headers, data=file_data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('\n FITXATEGIAK TRANSFERITU DIRA')

    def delete_file(self, file_path):

        print("/delete_file " + file_path)

        uri = 'https://api.dropboxapi.com/2/files/delete_v2'

        data = {'path': file_path}

        data_json = json.dumps(data)

        headers = {'Host': 'api.dropboxapi.com',
                        'Authorization': 'Bearer ' + self._access_token,
                        'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('\n FITXATEGIA EZABATU DA')

    def create_folder(self, path):

        print("/create_folder " + path)

        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'

        data = {'path': path, 'autorename"': False}

        data_json = json.dumps(data)

        headers = {'Host': 'api.dropboxapi.com',
                   'Authorization': 'Bearer ' + self._access_token,
                   'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('\n KARPETA SORTU DA')

    def move(self, fromPath, toPath):

        print("\n/move_file from " + fromPath + " to " + toPath)

        uri = 'https://api.dropboxapi.com/2/files/move_v2'
        data = {'allow_ownership_transfer': False,
                    'allow_shared_folder': False,
                    'autorename': False,
                    'from_path': fromPath,
                    'to_path': toPath}

        data_json = json.dumps(data)

        headers = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data,
                      allow_redirects=False)

        status = response.status_code
        content = response.content

        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('FITXATEGIA MUGITU DA')
        elif status == 409:
            print('ERRORE BAT SUERTATU DA, KONPROBATU PATH-A ONDO JARRITA DAGOELA (EMANDAKO FORMATOAN)'
                  '\n BALITEKE ERE MUGITZEKO FITXATEGIRIK HAUTATU EZ IZANA')
        return status

    def copy(self, fromPath, toPath):

        print("\n/copy_file from " + fromPath + " to " + toPath)

        uri = 'https://api.dropboxapi.com/2/files/copy_v2'

        data = {'allow_ownership_transfer': False,
                      'allow_shared_folder': False,
                      'autorename': False,
                      'from_path': fromPath,
                      'to_path': toPath}

        data_json = json.dumps(data)
        headers = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data_json,
                      allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('FITXATEGIA KOPIATU DA')
        elif status == 409:
            print('ERRORE BAT SUERTATU DA, KONPROBATU PATH-A ONDO JARRITA DAGOELA (EMANDAKO FORMATOAN)'
                  '\n BALITEKE ERE KOPIATZEKO FITXATEGIRIK HAUTATU EZ IZANA')
        return status

    def share(self, path, email):

        print("\n/add_file_member " + path)

        uri = 'https://api.dropboxapi.com/2/sharing/add_file_member'

        data = {'access_level': 'viewer',
                      'add_message_as_comment': True,
                      'custom_message': 'I shared this document with you:',
                      'file': path,
                      'members': [{'.tag': 'email', 'email': email}],
                      'quiet': False}

        data_json = json.dumps(data)

        headers = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}

        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('PARTEKATU DA FITXATEGIA')

    def download_zip(self, path):

        print("\n/download_zip " + path)

        uri = 'https://content.dropboxapi.com/2/files/download_zip'

        data = {'path': path}

        data_json = json.dumps(data)

        headers = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Dropbox-API-Arg': data}

        response = requests.post(uri, headers=headers, data=data_json, allow_redirects=False)

        status = response.status_code
        content = response.content
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            zip = open(path.split('/')[-1] + '.zip', 'wb')
            zip.write(content)
            zip.close()
            print('KARPETAREN ZIP-A JEITSI DA')
