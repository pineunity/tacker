# Copyright 2017 OpenStack Foundation
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

import sys
import time

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
from oslo_service import service
from oslo_utils import timeutils
from sqlalchemy.orm import exc as orm_exc

from tacker.common import topics
from tacker import context as t_context
from tacker.db.common_services import common_services_db
from tacker.db.nfvo import nfvo_db
from tacker.db.nfvo import  vnffg_db
from tacker.extensions import nfvo
from tacker.plugins.common import constants
from tacker import manager
from tacker import service as tacker_service
from tacker import version


LOG = logging.getLogger(__name__)


class Conductor(manager.Manager):
    def __init__(self, host, conf=None):
        if conf:
            self.conf = conf
        else:
            self.conf = cfg.CONF
        super(Conductor, self).__init__(host=self.conf.host)

    def update_vim(self, context, vim_id, status):
        t_admin_context = t_context.get_admin_context()
        update_time = timeutils.utcnow()
        with t_admin_context.session.begin(subtransactions=True):
            try:
                query = t_admin_context.session.query(nfvo_db.Vim)
                query.filter(
                    nfvo_db.Vim.id == vim_id).update(
                        {'status': status,
                         'updated_at': update_time})
            except orm_exc.NoResultFound:
                raise nfvo.VimNotFoundException(vim_id=vim_id)
            event_db = common_services_db.Event(
                resource_id=vim_id,
                resource_type=constants.RES_TYPE_VIM,
                resource_state=status,
                event_details="",
                event_type=constants.RES_EVT_MONITOR,
                timestamp=update_time)
            t_admin_context.session.add(event_db)
        return status

    def vnf_scaling_event(self, context, vnf_id):
        # check VNFFGs or NSs which VNFs belong to

        LOG.debug('vnf scaling event called sucesfully: %s', vnf_id)
        while(True):
            time.sleep(300)
            try:
                vnfm_plugin = manager.TackerManager.get_service_plugins()['VNFM']
                vnf_info = vnfm_plugin.get_vnf(context, vnf_id)
                if vnf_info['status'] == constants.ACTIVE:
                    break
            except Exception as e:
                LOG.error("Call vnf % is failed", vnf_id)




        # t_admin_context = t_context.get_admin_context()
        # vnfm_plugin = manager.TackerManager.get_service_plugins()['VNFM']
        # vnf = vnfm_plugin.g
        # et_vnf_resources(t_admin_context, vnf_id)
        # with t_admin_context.session.begin(subtransactions=True):
        #     try:
        #         query = t_admin_context.session.query(vnffg_db.Vnffg)
        #         query.filter(
        #             nfvo_db.Vim.id == vim_id).update(
        #                 {'status': status,
        #                  'updated_at': update_time})
        #
        # return vnffg_id or ns_id
        # action: in or out

        # check state pending_scale_out_in, pending_scale_out become active

        return vnf_id

    def vnf_respawning_event(self, context, vnf_id):
        # case 2: Auto-healing support
        # check VNFFGs or NSs which VNFs belong to

        LOG.debug('vnf respawning event called sucesfully: %s', vnf_id)

        while (True):
            time.sleep(300)
            try:
                vnfm_plugin = manager.TackerManager.get_service_plugins()['VNFM']
                vnf_info = vnfm_plugin.get_vnf(context, vnf_id)
                if vnf_info['status'] == constants.ACTIVE:
                    break
            except Exception as e:
                LOG.error("Call vnf % is failed", vnf_id)


        # t_admin_context = t_context.get_admin_context()
        # vnfm_plugin = manager.TackerManager.get_service_plugins()['VNFM']
        # vnf = vnfm_plugin.get_vnf_resources(t_admin_context, vnf_id)
        # nfvo_plugin = manager.TackerManager.get_service_plugins('NFVO')
        # vnffg = nfvo_plugin.get_vnffg_list(t_admin_context)


        # with t_admin_context.session.begin(subtransactions=True):
        #    try:
        #        query = t_admin_context.session.query(vnffg_db.Vnffg)
        #        vnffg_list = query.filter(vnffg_db.Vnffg.vnf_mapping)

        # check pending_create for resoawnng action until become active

        return vnf_id
        # return vnffg_id or ns_id


def init(args, **kwargs):
    cfg.CONF(args=args, project='tacker',
             version='%%prog %s' % version.version_info.release_string(),
             **kwargs)

    # FIXME(ihrachys): if import is put in global, circular import
    # failure occurs
    from tacker.common import rpc as n_rpc
    n_rpc.init(cfg.CONF)


def main(manager='tacker.conductor.conductor_server.Conductor'):
    init(sys.argv[1:])
    logging.setup(cfg.CONF, "tacker")
    oslo_messaging.set_transport_defaults(control_exchange='tacker')
    logging.setup(cfg.CONF, "tacker")
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)
    server = tacker_service.Service.create(
        binary='tacker-conductor',
        topic=topics.TOPIC_CONDUCTOR,
        manager=manager)
    service.launch(cfg.CONF, server).wait()
