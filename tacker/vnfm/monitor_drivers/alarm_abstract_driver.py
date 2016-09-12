# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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
#    under the License.
#

import abc

import six

from tacker.api import extensions


@six.add_metaclass(abc.ABCMeta)
class VNFMonitorAbstractAlarmDriver(extensions.PluginInterface):

    @abc.abstractmethod
    def get_type(self):
        """Return one of predefined type of the hosting vnf drivers."""
        pass

    @abc.abstractmethod
    def get_name(self):
        """Return a symbolic name for the VNF Monitor plugin."""
        pass

    @abc.abstractmethod
    def get_description(self):
        """Return description of VNF Monitor plugin."""
        pass

    @abc.abstractmethod
    def call_alarm_url(self, vnf, kwargs):
        """Monitor.

        Get alarm url from the low-level design


        :param plugin:
        :param vnf:
        """
        pass

    @abc.abstractmethod
    def process_alarm(self, plugin, vnf):
        """Monitor.

        Process alarm url from the low-level design


        :param plugin:
        :param vnf:
        """
        pass

    def process_notification(self, plugin, vnf):
        """Notification.

        Send messages to Tacker users


        :param plugin:
        :param vnf:
        """
        pass
