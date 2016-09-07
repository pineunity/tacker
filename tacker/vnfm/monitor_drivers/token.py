#    Copyright 2012 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import keystoneclient.v3.client as ks_client


class Token(object):
    def __init__(self, username, password, auth_url, tenant_name):
        self.username = username
        self.password = password
        self.auth_url = auth_url
        self.tenant_name = tenant_name

    def create_token(self):
        keystone = ks_client.Client(username=self.username,
                                   password=self.password,
                                   auth_url=self.auth_url,
                                   tenant_name=self.tenant_name)

        token = keystone.auth_ref['token']['id']
        return token
