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

from tacker._i18n import _LW
from tacker.agent.linux import utils as linux_utils
from tacker.common import log
from tacker.vm.monitor_drivers import abstract_alarm_driver

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt('period', default='60',
               help=_('period time')),
    cfg.StrOpt('evaluation_period', default='1',
               help=_('evaluation period')),
    cfg.StrOpt('threshold', default='70',
               help=_('threshold'))
]
cfg.CONF.register_opts(OPTS, 'ceilometer_driver')


def config_opts():
    return [('ceilometer_driver', OPTS)]


class VNFMonitorCeilometer(abstract_alarm_driver.VNFMonitorAbstractAlarmDriver):
    def get_type(self):
        return 'Ceiloemter'

    def get_name(self):
        return 'Ceilometer'

    def get_description(self):
        return 'Tacker VNFMonitor Ceilometer Driver'

    def monitor_url(self, plugin, context, device):
        LOG.debug(_('monitor_url %s'), device)
        return device.get('monitor_url', '')

    def _is_pingable(self, mgmt_ip="", count=5, timeout=1, interval='0.2',
                     **kwargs):
        """Checks whether an IP address is reachable by pinging.

        Use linux utils to execute the ping (ICMP ECHO) command.
        Sends 5 packets with an interval of 0.2 seconds and timeout of 1
        seconds. Runtime error implies unreachability else IP is pingable.
        :param ip: IP to check
        :return: bool - True or string 'failure' depending on pingability.
        """
        ping_cmd = ['ping',
                    '-c', count,
                    '-W', timeout,
                    '-i', interval,
                    mgmt_ip]

        try:
            linux_utils.execute(ping_cmd, check_exit_code=True)
            return True
        except RuntimeError:
            LOG.warning(_LW("Cannot ping ip address: %s"), mgmt_ip)
            return 'failure'
    def create_alarm(self, plugin, device):
        alarm_url ={}
        return alarm_url


    @log.log
    def monitor_call(self, device, kwargs):
        if not kwargs['mgmt_ip']:
            return

        return self._is_pingable(**kwargs)
