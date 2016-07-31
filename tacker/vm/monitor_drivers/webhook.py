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
import time
import random
import string
import socket
from oslo_config import cfg
from oslo_log import log as logging
from tacker.db.vm import vm_db

LOG = logging.getLogger(__name__)

trigger_opts = [
    cfg.StrOpt('host', socket.gethostname(),
               help=_('Address which drivers use to trigger')),
    cfg.PortOpt('port', default=9890,
               help=_('number of seconds to wait for a response')),
]
cfg.CONF.register_opts(trigger_opts, group='trigger')

DRIVER = ['Ceilometer', 'Monasca', 'StackStorm']
class Webhook(object):
    def __init__(self,driver):
        self.driver = driver

    def create_alrm_url(self, plugin, device):
        # url: 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name/key'
        host = cfg.CONF.trigger.host
        port = cfg.CONF.trigger.port
        #host = 'pinedcn'
        #port = '9890'
        # vnf-id?
        # policy_name?
        # action?
        host_port = {'host': host, 'port': port}
        LOG.info(_("Tacker in heat listening on %(host)s:%(port)s"),
                 {'host': host,
                  'port': port})
        origin = "http://%(host)s:%(port)/vnfs" % host_port
#        monitoring_policy_name = policy_name
#                    alarm_action_name = policy_dict['triggers']['resize_compute']['action']
#                    access_key = ''.join(
#                        random.SystemRandom().choice(string.ascii_lowercase + string.digits)
#                        for _ in range(8))
#                    alarm_url = "".join([origin, vnf_id, monitoring_policy_name, alarm_action_name, '?', access_key])

        if self.driver in DRIVER:
            alarm_url = {}
            return alarm_url