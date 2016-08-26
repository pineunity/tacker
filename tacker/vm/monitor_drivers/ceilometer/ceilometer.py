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
import yaml
from oslo_config import cfg
from oslo_log import log as logging

from tacker._i18n import _LW
from tacker.common import log
from tacker.vm.monitor_drivers import alarm_abstract_driver


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


class VNFMonitorCeilometer(alarm_abstract_driver.VNFMonitorAbstractAlarmDriver):
    def get_type(self):
        return 'Ceiloemter'

    def get_name(self):
        return 'Ceilometer'

    def get_description(self):
        return 'Tacker VNFMonitor Ceilometer Driver'

    def monitor_url(self, plugin, context, device):
        LOG.debug(_('monitor_url %s'), device)
        return device.get('monitor_url', '')

    def _is_alarmed(self, device, **kwargs):
        """Checks whether a VM reaches to threshold.
        threshold gets from device
        :param device
        :return: bool - string 'resize_compute' when reaching threshold
        Check if device[id]==vnn-id --> device
        call wsgi function
        """
        vnfd_yaml = device['template_dict']['attribute']['vnfd']
        vnfd_dict = yaml.load(vnfd_yaml)



        LOG.warning(_LW("Device %s is reaching to threshold"), device['id'])

        return 'resize_compute'

    def get_alarm_url(self, plugin, device):
        url = ''

        return url
    @log.log
    def monitor_call(self, device, kwargs):
        if not kwargs['mgmt_ip']:
            return

        return self._is_pingable(**kwargs)
