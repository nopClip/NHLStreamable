import requests
import json

BASE_URL = 'https://api.streamable.com/'
API_PATH = {
    'upload': 'upload',
    'import': 'import?url=',
    'users': 'users/',
    'me': 'me'
}
USER = 'YOUR STREAMABLE EMAIL'
PASS = 'YOUR STREAMABLE PASSWORD'


class Streamable:
    """Wrapper for the Streamable API"""

    def __init__(self):
        """Check if Streamable user account is configured"""
        self.auth = self.check_auth()

    def check_auth(self):
        """Check if Streamable user account is configured

        Streamable allows both authenticated and unauthenticated (anonymous) uploads

        :returns: tuple if True, which sets auth=(USER, PASS)
        :returns: None if False, which sets auth=None
        ..note:: Data must be formatted this way for the requests module

        """
        if USER and PASS:
            return (USER, PASS)
        else:
            return None

    def upload(self, file, title=''):
        """Uploads a video file to Streamable

        :param file: The video file to upload (string)
        :param title: The optional title of the video (string)
        :returns: Response object from server

        """
        url = BASE_URL + API_PATH['upload']
        vid_file = {'file': open(file, 'rb')}
        print('Uploading...')
        resp = requests.post(url, files=vid_file, auth=self.auth, data={'title': title})
        return self.result(resp)

    def import_vid(self, url, title=''):
        """Imports a video to Streamable from a URL

        :param url: The URL of the video to import (string)
        :param title: The optional title of the video (string)
        :returns: Response object from server

        """
        print('Uploading...')
        url = BASE_URL + API_PATH['import'] + url
        resp = requests.get(url, auth=self.auth, data={'title': title})
        return self.result(resp)

    def get_user(self, user):
        """Returns a User object representing the requested user

        :param user: The requested user (string)

        """
        print(f'Retrieving user {user}...')
        url = BASE_URL + API_PATH['users'] + user
        resp = requests.get(url, auth=self.auth)
        return self.result(resp)

    def get_me(self):
        """Returns a User object representing the currently authenticated user"""
        if not self.auth:
            print('\n[!] Error - authentication required\n')
            return
        print(f'Retrieving user {USER}...')
        url = BASE_URL + API_PATH['me']
        resp = requests.get(url, auth=self.auth)
        return self.result(resp)

    def result(self, resp):
        """Handle the response object from the server

        :param resp: The response object

        ..note:: Requests module has built in .json(), but we're using the
                 standard library json.dumps to pretty print to terminal.

        """
        #print(f'\n{resp.status_code} - {resp.reason}\n')
        if resp.status_code in [401, 402, 404]:
            return
        #print(json.dumps(resp.json(), indent=4))
        return resp.json()

if __name__ == '__main__':

    streamable = Streamable()
    # streamable.upload(file='', title='Test upload')
    # streamable.import_vid(url='', title='Test import')
    # streamable.get_user(user='')
    # streamable.get_me()
