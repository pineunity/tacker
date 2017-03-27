# All Rights Reserved.
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

import abc
import six

from tacker.api import extensions


@six.add_metaclass(abc.ABCMeta)
class ActionPolicyAbstractDriver(extensions.PluginInterface):
    @classmethod
    @abc.abstractmethod
    def execute_action(cls, plugin, vnf_dict):
        pass

    _POLICIES = {}

    @staticmethod
    def register(policy, infra_driver=None):
        def _register(cls):
            cls._POLICIES.setdefault(policy, {})[infra_driver] = cls
            return cls
        return _register

    @classmethod
    def get_policy(cls, policy, infra_driver=None):
        action_clses = cls._POLICIES.get(policy)
        if not action_clses:
            return None
        cls = action_clses.get(infra_driver)
        if cls:
            return cls
        return action_clses.get(None)

    @classmethod
    def get_supported_actions(cls):
        return cls._POLICIES.keys()
