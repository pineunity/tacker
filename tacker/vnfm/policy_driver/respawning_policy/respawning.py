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

from tacker import context as t_context
from tacker.db.common_services import common_services_db
from tacker.plugins.common import constants
from tacker.vnfm.infra_drivers.openstack import heat_client as hc
from tacker.vnfm.policy_driver import abstract_driver
from tacker.vnfm import vim_client

LOG = logging.getLogger(__name__)


def _log_monitor_events(context, vnf_dict, evt_details):
    _cos_db_plg = common_services_db.CommonServicesPluginDb()
    _cos_db_plg.create_event(context, res_id=vnf_dict['id'],
                             res_type=constants.RES_TYPE_VNF,
                             res_state=vnf_dict['status'],
                             evt_type=constants.RES_EVT_MONITOR,
                             tstamp=timeutils.utcnow(),
                             details=evt_details)


@abstract_driver.ActionPolicyAbstractDriver.register('respawn', 'openstack')
class VNFPolicyLogging(abstract_driver.ActionPolicyAbstractDriver):
    @classmethod
    def execute_action(cls, plugin, vnf_dict):
        vnf_id = vnf_dict['id']
        LOG.info(_('vnf %s is dead and needs to be respawned'), vnf_id)
        attributes = vnf_dict['attributes']
        vim_id = vnf_dict['vim_id']
        # TODO(anyone) set the current request ctxt
        context = t_context.get_admin_context()

        def _update_failure_count():
            failure_count = int(attributes.get('failure_count', '0')) + 1
            failure_count_str = str(failure_count)
            LOG.debug(_("vnf %(vnf_id)s failure count %(failure_count)s"),
                      {'vnf_id': vnf_id, 'failure_count': failure_count_str})
            attributes['failure_count'] = failure_count_str
            attributes['dead_instance_id_' + failure_count_str] = vnf_dict[
                'instance_id']

        def _fetch_vim(vim_uuid):
            return vim_client.VimClient().get_vim(context, vim_uuid)

        def _delete_heat_stack(vim_auth):
            placement_attr = vnf_dict.get('placement_attr', {})
            region_name = placement_attr.get('region_name')
            heatclient = hc.HeatClient(auth_attr=vim_auth,
                                       region_name=region_name)
            heatclient.delete(vnf_dict['instance_id'])
            LOG.debug(_("Heat stack %s delete initiated"), vnf_dict[
                'instance_id'])
            _log_monitor_events(context, vnf_dict, "ActionRespawnHeat invoked")

        def _respin_vnf():
            update_vnf_dict = plugin.create_vnf_sync(context, vnf_dict)
            LOG.info(_('respawned new vnf %s'), update_vnf_dict['id'])
            plugin.config_vnf(context, update_vnf_dict)
            return update_vnf_dict

        if plugin._mark_vnf_dead(vnf_dict['id']):
            _update_failure_count()
            vim_res = _fetch_vim(vim_id)
            if vnf_dict['attributes'].get('monitoring_policy'):
                plugin._vnf_monitor.mark_dead(vnf_dict['id'])
                _delete_heat_stack(vim_res['vim_auth'])
                updated_vnf = _respin_vnf()
                plugin.add_vnf_to_monitor(updated_vnf, vim_res['vim_type'])
                LOG.debug(_("VNF %s added to monitor thread"), updated_vnf[
                    'id'])
            if vnf_dict['attributes'].get('alarming_policy'):
                _delete_heat_stack(vim_res['vim_auth'])
                vnf_dict['attributes'].pop('alarming_policy')
                _respin_vnf()
