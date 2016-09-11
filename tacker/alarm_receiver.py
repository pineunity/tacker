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
import logging
import os
from oslo_serialization import jsonutils
from six.moves.urllib import parse as urlparse
from tacker.vnfm.monitor_drivers.token import Token
from tacker import wsgi
# check alarm url with db --> move to plugin

LOG = logging.getLogger(__name__)

# Getting keystone auth credentials from env
username = os.getenv('OS_USERNAME')
password = os.getenv('OS_PASSWORD')
project_name = os.getenv('OS_PROJECT_NAME')


class AlarmReceiver(wsgi.Middleware):
    def process_request(self, req):
        if req.method != 'POST' or not self.handle_url(req.url):
            return
        prefix, info, params = self.handle_url(req.url)
        LOG.debug('token in receiver: %(username)s %(password)s %(project_name)',
                  {'username':username,'password': password, 'project_name': project_name})
        token = Token(username, password,
                      project_name, auth_url="http://localhost:35357/v3")
        token_identity = token.create_token()
        req.headers['X_AUTH_TOKEN'] = token_identity
        # Change the body request
        if 'alarm_id' in req.body:
            body_dict = dict()
            body_dict['trigger'] = {}
            body_dict['trigger'].setdefault('params', {})
            # Update params in the body request
            alarm_dict = jsonutils.loads(req.body)
            body_dict['trigger']['params']['alarm'] = alarm_dict
            body_dict['trigger']['params']['credential'] = info[6]
            # Update policy and action
            body_dict['trigger']['policy_name'] = info[4]
            body_dict['trigger']['action_name'] = info[5]
            req.body = jsonutils.dumps(body_dict)
            LOG.debug('Body alarm: %s', req.body)
        # Need to change url because of mandatory
        req.environ['PATH_INFO'] = prefix + 'actions'
        req.environ['QUERY_STRING'] = ''
        LOG.debug('alarm url in receiver: %s', req.url)

    def handle_url(self, url):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/mon-policy-name/action-name/8ef785' # noqa
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')
        if len(p) != 7:
            return None

        if any((p[0] != '', p[2] != 'vnfs')):
            return None
        qs = urlparse.parse_qs(parts.query)
        params = dict((k, v[0]) for k, v in qs.items())
        prefix_url = '/%(collec)s/%(vnf_uuid)s/' % {'collec': p[2],
                                                    'vnf_uuid': p[3]}
        return prefix_url, p, params
