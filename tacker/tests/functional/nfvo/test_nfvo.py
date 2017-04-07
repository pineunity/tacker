# Copyright 2016 Brocade Communications System, Inc.
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

import yaml

from oslo_config import cfg
from tackerclient.common import exceptions

from tacker.plugins.common import constants as evt_constants
from tacker.tests import constants
from tacker.tests.functional import base
from tacker.tests.utils import read_file

import time
CONF = cfg.CONF


class NsdTestCreate(base.BaseTackerTest):
    def _test_create_tosca_vnfd(self, tosca_vnfd_file, vnfd_name):
        input_yaml = read_file(tosca_vnfd_file)
        tosca_dict = yaml.safe_load(input_yaml)
        tosca_arg = {'vnfd': {'name': vnfd_name,
                              'attributes': {'vnfd': tosca_dict}}}
        vnfd_instance = self.client.create_vnfd(body=tosca_arg)
        self.assertEqual(vnfd_instance['vnfd']['name'], vnfd_name)
        self.assertIsNotNone(vnfd_instance)

        vnfds = self.client.list_vnfds().get('vnfds')
        self.assertIsNotNone(vnfds, "List of vnfds are Empty after Creation")
        return vnfd_instance['vnfd']['id']

    def _test_create_nsd(self, tosca_nsd_file, nsd_name):
        input_yaml = read_file(tosca_nsd_file)
        tosca_dict = yaml.safe_load(input_yaml)
        tosca_arg = {'nsd': {'name': nsd_name,
                             'attributes': {'nsd': tosca_dict}}}
        nsd_instance = self.client.create_nsd(body=tosca_arg)
        self.assertIsNotNone(nsd_instance)
        return nsd_instance['nsd']['id']

    def _test_delete_nsd(self, nsd_id):
        try:
            self.client.delete_nsd(nsd_id)
        except Exception:
                assert False, "nsd Delete failed"

    def _test_delete_vnfd(self, vnfd_id, timeout=constants.NS_DELETE_TIMEOUT):
        start_time = int(time.time())
        while True:
            try:
                self.client.delete_vnfd(vnfd_id)
            except exceptions.Conflict:
                time.sleep(2)
            except Exception:
                assert False, "vnfd Delete failed"
            else:
                break
            if (int(time.time()) - start_time) > timeout:
                assert False, "vnfd still in use"
        self.verify_vnfd_events(vnfd_id, evt_constants.RES_EVT_DELETE,
                                evt_constants.RES_EVT_NA_STATE)

    def _wait_until_ns_status(self, ns_id, target_status, timeout,
                              sleep_interval):
        start_time = int(time.time())
        while True:
                ns_result = self.client.show_ns(ns_id)
                status = ns_result['ns']['status']
                if (status == target_status) or (
                        (int(time.time()) - start_time) > timeout):
                    break
                time.sleep(sleep_interval)

        self.assertEqual(status, target_status,
                         "ns %(ns_id)s with status %(status)s is"
                         " expected to be %(target)s" %
                         {"ns_id": ns_id, "status": status,
                          "target": target_status})

    def _wait_until_ns_delete(self, ns_id, timeout):
        start_time = int(time.time())
        while True:
            try:
                ns_result = self.client.show_ns(ns_id)
                time.sleep(2)
            except Exception:
                return
            status = ns_result['ns']['status']
            if (status != 'PENDING_DELETE') or ((
                    int(time.time()) - start_time) > timeout):
                raise Exception("Failed with status: %s" % status)

    def _test_create_delete_ns(self, nsd_file, ns_name,
                               vnfd1_file, vnfd1_name,
                               vnfd2_file, vnfd2_name):
        vnfd1_id = self._test_create_tosca_vnfd(vnfd1_file, vnfd1_name)
        vnfd2_id = self._test_create_tosca_vnfd(vnfd2_file, vnfd2_name)
        nsd_name = ns_name + '-nsd'
        nsd_id = self._test_create_nsd(
            nsd_file, nsd_name)
        ns_arg = {'ns': {'nsd_id': nsd_id, 'name': ns_name,
                  'attributes': {"param_values": {"nsd":
                                {"vl2_name": "net0",
                                 "vl1_name": "net_mgmt"}}}}}
        ns_instance = self.client.create_ns(body=ns_arg)
        ns_id = ns_instance['ns']['id']
        self._wait_until_ns_status(ns_id, 'ACTIVE',
                                   constants.NS_CREATE_TIMEOUT,
                                   constants.ACTIVE_SLEEP_TIME)
        ns_show_out = self.client.show_ns(ns_id)['ns']
        self.assertIsNotNone(ns_show_out['mgmt_urls'])
        try:
            self.client.delete_ns(ns_id)
        except Exception:
            assert False, "ns Delete failed"
        self._wait_until_ns_delete(ns_id, constants.NS_DELETE_TIMEOUT)
        self._test_delete_nsd(nsd_id)
        self._test_delete_vnfd(vnfd1_id)
        self._test_delete_vnfd(vnfd2_id)

    def _test_create_delete_nsd(self, nsd_file, nsd_name,
                                vnfd1_file, vnfd1_name,
                                vnfd2_file, vnfd2_name):
        vnfd1_id = self._test_create_tosca_vnfd(vnfd1_file, vnfd1_name)
        vnfd2_id = self._test_create_tosca_vnfd(vnfd2_file, vnfd2_name)
        nsd_id = self._test_create_nsd(nsd_file, nsd_name)
        self._test_delete_nsd(nsd_id)
        self._test_delete_vnfd(vnfd1_id)
        self._test_delete_vnfd(vnfd2_id)

    def test_create_delete_nsd_simple(self,
                                      vnfd1_file='test-nsd-vnfd1.yaml',
                                      vnfd1_name='test-nsd-vnfd1',
                                      vnfd2_file='test-nsd-vnfd2.yaml',
                                      vnfd2_name='test-nsd-vnfd2'):
        self._test_create_delete_nsd('test-nsd.yaml', 'test-nsd',
                                     vnfd1_file, vnfd1_name,
                                     vnfd2_file, vnfd2_name)

    def test_create_delete_nsd_autoscaling(self,
                                           vnfd1_file='test-nsd-vnfd1-as.yaml',
                                           vnfd1_name='test-nsd-vnfd1-as',
                                           vnfd2_file='test-nsd-vnfd2-as.yaml',
                                           vnfd2_name='test-nsd-vnfd2-as'):
        self._test_create_delete_nsd('test-nsd-as.yaml', 'test-nsd-as',
                                     vnfd1_file, vnfd1_name,
                                     vnfd2_file, vnfd2_name)

    def test_create_delete_nsd_respawning(self,
                                          vnfd1_file='test-nsd-vnfd1-rs.yaml',
                                          vnfd1_name='test-nsd-vnfd1-rs',
                                          vnfd2_file='test-nsd-vnfd2-rs.yaml',
                                          vnfd2_name='test-nsd-vnfd2-rs'):
        self._test_create_delete_nsd('test-nsd-rs.yaml', 'test-nsd-rs',
                                     vnfd1_file, vnfd1_name,
                                     vnfd2_file, vnfd2_name)

    def test_create_delete_network_service_simple(self,
                                           vnfd1_file='test-ns-vnfd1.yaml',
                                           vnfd1_name='test-ns-vnfd1',
                                           vnfd2_file='test-ns-vnfd2.yaml',
                                           vnfd2_name='test-ns-vnfd2'):
        self._test_create_delete_ns('test-ns-nsd.yaml', 'test-ns',
                                    vnfd1_file, vnfd1_name,
                                    vnfd2_file, vnfd2_name)

    def test_create_delete_network_service_autoscaling(self,
                                           vnfd1_file='test-ns-vnfd1-as.yaml',
                                           vnfd1_name='test-ns-vnfd1-as',
                                           vnfd2_file='test-ns-vnfd2-as.yaml',
                                           vnfd2_name='test-ns-vnfd2-as'):
        self._test_create_delete_ns('test-ns-nsd-as.yaml', 'test-ns-as',
                                    vnfd1_file, vnfd1_name,
                                    vnfd2_file, vnfd2_name)

    def test_create_delete_network_service_respawning(self,
                                           vnfd1_file='test-ns-vnfd1-rs.yaml',
                                           vnfd1_name='test-ns-vnfd1-rs',
                                           vnfd2_file='test-ns-vnfd2-rs.yaml',
                                           vnfd2_name='test-ns-vnfd2-rs'):
        self._test_create_delete_ns('test-ns-nsd-rs.yaml', 'test-ns-rs',
                                    vnfd1_file, vnfd1_name,
                                    vnfd2_file, vnfd2_name)
