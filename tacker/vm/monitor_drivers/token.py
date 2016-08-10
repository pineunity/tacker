# authenticate with keystone to get a token
import keystoneclient.v2_0.client as ksclient

class Token(object):
    def __init__(self, username, password, auth_url, tenant_name):
        self.username = username
        self.password = password
        self.auth_url = auth_url
        self.tenant_name = tenant_name

    def create_token(self):
        keystone = ksclient.Client(auth_url=self.auth_url,
                           username=self.username,
                           password=self.username,
                           tenant_name=self.tenant_name)

        token = keystone.auth_ref['token']['id']
        return token
