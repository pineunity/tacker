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
from oslo_serialization import jsonutils
import copy
import logging
from six.moves.urllib import parse as urlparse
from tacker import wsgi
from tacker.vm.monitor_drivers.token import Token
# check alarm url with db --> move to plugin

LOG = logging.getLogger(__name__)

class AlarmReceiver(wsgi.Middleware):
    def process_request(self, req):
        if req.method != 'POST':
            return
        url = req.url
        if not self.handle_url(url):
            return
        LOG.debug(_('tung triggered: %s'), url)
        info, params = self.handle_url(req.url)
        device_id = info[3]
        self.validate_url(device_id)
        token = Token(username='admin', password='devstack',
                      auth_url="http://127.0.0.1:35357/v2.0", tenant_name="admin")
        token_identity = token.create_token()
        req.headers['X_AUTH_TOKEN'] = token_identity
        LOG.debug('Body alarm: %s', req.body)
        if 'alarm_id' in req.body:
            body_dict = dict()
            body_dict['trigger'] = {}
            body_dict['trigger']['params'] = jsonutils.loads(req.body)
            body_dict['trigger']['policy_name'] = info[4]
            body_dict['trigger']['action_name'] = info[5]
            req.body = jsonutils.dumps(body_dict)
            LOG.debug('Body alarm: %s', req.body)

    def handle_url(self, url):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name?key=8785'
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')
        # expected: ['', 'v1.0', 'vnfs', 'vnf-uuid', 'monitoring-policy-name', 'action-name']
        if len(p) != 6:
            return None

        if any((p[0] != '', p[2] != 'vnfs')):
            return None
        qs = urlparse.parse_qs(parts.query)
        params = dict((k, v[0]) for k, v in qs.items())
        return p, params

    def validate_url(self, device_id):
        '''Validate with db'''
        LOG.debug(_('Alarm url triggered: %s'), device_id)
        return True
