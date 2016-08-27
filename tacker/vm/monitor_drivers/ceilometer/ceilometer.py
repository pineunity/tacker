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
#

from oslo_config import cfg
from oslo_log import log as logging
import random
import string
from tacker.common import log
from tacker.common import utils
from tacker._i18n import _LW
from tacker.vm.monitor_drivers import alarm_abstract_driver


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


class VNFMonitorCeilometer(alarm_abstract_driver.VNFMonitorAbstractAlarmDriver):
    def get_type(self):
        return 'Ceiloemter'

    def get_name(self):
        return 'Ceilometer'

    def get_description(self):
        return 'Tacker VNFMonitor Ceilometer Driver'

    def _create_alarm_url(self, vnf_id, mon_policy_name, mon_policy_action):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name?key=8785'
        host = cfg.CONF.trigger.host
        port = cfg.CONF.trigger.port
        LOG.info(_("Tacker in heat listening on %(host)s:%(port)s"),
                 {'host': host,
                  'port': port})
        origin = "http://%(host)s:%(port)s/v1.0/vnfs" % {'host': host, 'port': port}
        access_key = ''.join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(8))
        alarm_url = "".join([origin, '/', vnf_id, '/', mon_policy_name, '/',
                             mon_policy_action, '/', access_key])
        return alarm_url

    def get_alarm_url(self, device, kwargs):
        '''must be used after call heat-create in plugin'''
        return self._create_alarm_url(**kwargs)
