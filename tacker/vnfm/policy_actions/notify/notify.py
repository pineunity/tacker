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

from oslo_log import log as logging
from oslo_utils import timeutils

from tacker.db.common_services import common_services_db_plugin
from tacker.plugins.common import constants
from tacker.vnfm.policy_actions import abstract_action

LOG = logging.getLogger(__name__)


def _log_monitor_events(context, vnf_dict, evt_details):
    _cos_db_plg = common_services_db_plugin.CommonServicesPluginDb()
    _cos_db_plg.create_event(context, res_id=vnf_dict['id'],
                             res_type=constants.RES_TYPE_VNF,
                             res_state=vnf_dict['status'],
                             evt_type=constants.RES_EVT_MONITOR,
                             tstamp=timeutils.utcnow(),
                             details=evt_details)


class VNFActionNotify(abstract_action.AbstractPolicyAction):
    def get_type(self):
        return 'notify'

    def get_name(self):
        return 'notify'

    def get_description(self):
        return 'Tacker VNF notification policy'

    def execute_action(self, plugin, context, vnf_dict, args):
        # Let args be like actions: DEFAULT_ALARM_ACTIONS
        vnf_id = vnf_dict['id']
        _log_monitor_events(context,
                            vnf_dict,
                            "ActionAutoscalingHeat invoked")

        if args in constants.DEFAULT_ALARM_ACTIONS:
            from tacker.conductor.conductorrpc import AutoHealingRPC
            return
        else:
            from tacker.conductor.conductorrpc import AutoScalingRPC

        def _update(self, status):
            LOG.info("VIM %s changed to status %s", self.vim_id, status)
            target = vim_monitor_rpc.VIMUpdateRPC.target
            rpc_client = rpc.get_client(target)
            cctxt = rpc_client.prepare()
            return cctxt.call(t_context.get_admin_context_without_session(),
                              'update_vim',
                              vim_id=self.vim_id,
                              status=status)

        def run(self):
            servers = []
            try:
                rpc.init_action_rpc(cfg.CONF)
                servers = self.start_rpc_listeners()
            except Exception:
                LOG.exception('failed to start rpc in vim action')
                return 'FAILED'
            try:
                while True:
                    if self.killed:
                        break
                    status = self._ping()
                    if self.current_status != status:
                        self.current_status = self._update(status)
                        # TODO(gongysh) If we need to sleep a little time here?
            except Exception:
                LOG.exception('failed to run mistral action for vim %s',
                              self.vim_id)
                return 'FAILED'
            # to stop rpc connection
            for server in servers:
                try:
                    server.stop()
                except Exception:
                    LOG.exception(
                        'failed to stop rpc connection for vim %s',
                        self.vim_id)
            return 'KILLED'

        def test(self):
            return 'REACHABLE'
