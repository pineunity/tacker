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
from oslo_config import cfg
from oslo_serialization import jsonutils
import logging
from six.moves.urllib import parse as urlparse
from tacker import wsgi
from tacker.vnfm.monitor_drivers.token import Token
# check alarm url with db --> move to plugin

LOG = logging.getLogger(__name__)

core_opts = [
            cfg.StrOpt('username', default='tacker',
                       help=('Username to use for tacker API requests')),
            cfg.StrOpt('password', default = 'devstack',
                       help=('Password to use for tacker API requests')),
            cfg.StrOpt('project_name', default='service',
                       help=('Project name to use for tacker API requests')),
            cfg.StrOpt('auth_uri', default='http://127.0.0.1:5000',
                       help=('The keystone auth URI')),
        ]

ks_authtoken = cfg.OptGroup(name='ks_authtoken',
                                          title='keystone options for alarm request')
# Register the configuration options
cfg.CONF.register_opts(core_opts, group=ks_authtoken)


class AlarmReceiver(wsgi.Middleware):
    def process_request(self, req):
        if req.method != 'POST':
            return
        url = req.url
        if not self.handle_url(url):
            return
        LOG.debug(_('tung triggered: %s'), url)
        prefix, info, params = self.handle_url(req.url)
        LOG.debug(_('tung triggered: %s'), prefix)
        username = cfg.CONF.ks_authtoken.username
        password = cfg.CONF.ks_authtoken.password
        auth_url = cfg.CONF.ks_authtoken.auth_uri + "/v3"
        project_name = cfg.CONF.ks_authtoken.project_name
        token = Token(username, password,
                      auth_url, project_name)
        token_identity = token.create_token()
        req.headers['X_AUTH_TOKEN'] = token_identity
        LOG.debug('Body alarm before parsing: %s', req.body)
        # Change the body request
        if req.body:
            body_dict = dict()
            body_dict['trigger'] = {}
            body_dict['trigger'].setdefault('params', {})
            # Update params in the body request
            body_info = jsonutils.loads(req.body)
            body_dict['trigger']['params']['data'] = body_info
            body_dict['trigger']['params']['credential'] = info[6]
            # Update policy and action
            body_dict['trigger']['policy_name'] = info[4]
            body_dict['trigger']['action_name'] = info[5]
            req.body = jsonutils.dumps(body_dict)
            LOG.debug('Body alarm: %s', req.body)
        # Need to change url because of mandatory
        req.environ['PATH_INFO'] = prefix + 'actions'
        LOG.debug(_('tung triggered: %s'), req.environ['PATH_INFO'])
        req.environ['QUERY_STRING'] = ''
        LOG.debug('alarm url in receiver: %s', req.url)

    def handle_url(self, url):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name/8785'
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')
        # expected: ['', 'v1.0', 'vnfs', 'vnf-uuid', 'monitoring-policy-name', 'action-name', '8785']
        if len(p) != 7:
            return None

        if any((p[0] != '', p[2] != 'vnfs')):
            return None
        qs = urlparse.parse_qs(parts.query)
        params = dict((k, v[0]) for k, v in qs.items())
        prefix_url = '/%(collec)s/%(vnf_uuid)s/' % {'collec': p[2], 'vnf_uuid': p[3]}
        return prefix_url, p, params

