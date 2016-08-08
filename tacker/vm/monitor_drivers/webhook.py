# Copyright 2015 Intel Corporation.
# All Rights Reserved.
#
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
#    under the License
# import time
import random
import string
from oslo_config import cfg
from oslo_log import log as logging
from tacker.common import utils
from six.moves.urllib import parse as urlparse
from collections import OrderedDict
# from tacker.db.vm import vm_db

LOG = logging.getLogger(__name__)

trigger_opts = [
    cfg.StrOpt('host', default=utils.get_hostname(),
               help=_('Address which drivers use to trigger')),
    cfg.PortOpt('port', default=9890,
               help=_('number of seconds to wait for a response'))
]
cfg.CONF.register_opts(trigger_opts, group='trigger')

def config_opts():
    return [('trigger', trigger_opts)]

DRIVER = ['Ceilometer', 'Monasca', 'StackStorm']


class Webhook(object):
    def __init__(self, driver):
        self.driver = driver

    def create_alarm_url(self, policy_name, policy_dict, device):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name?key=8785'

        host = cfg.CONF.trigger.host
        port = cfg.CONF.trigger.port
        host_port = {'host': host, 'port': port}
        LOG.info(_("Tacker in heat listening on %(host)s:%(port)s"),
                 {'host': host,
                  'port': port})
        origin = "http://%(host)s:%(port)s/v1.0/vnfs" % {'host': host, 'port': port}
        vnf_id = device['id']
        monitoring_policy_name = policy_name
        alarm_action_name = policy_dict['triggers']['resize_compute']['action']['resize_compute']
        access_key = ''.join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(8))
        # params = OrderedDict(policy_name=monitoring_policy_name, action_name=alarm_action_name, key=access_key)
        params = OrderedDict([('policy_name', monitoring_policy_name),
                              ('action_name', alarm_action_name), ('key', access_key)])
        query = urlparse.urlencode(params)
        # params = {'key':access_key}
        ordered_params = sorted(params.items(), key=lambda t: t[0])
        # alarm_url = "".join([origin, '/', vnf_id, '/', monitoring_policy_name, '/',
        #                      alarm_action_name, '?', urlparse.urlencode(ordered_params)])
        alarm_url = "".join([origin, '/', vnf_id, '?', query])
        if self.driver in DRIVER:
            return alarm_url
