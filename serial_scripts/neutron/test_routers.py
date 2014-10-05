# Need to import path to test/fixtures and test/scripts/
# Ex : export PYTHONPATH='$PATH:/root/test/fixtures/:/root/test/scripts/'
#
# To run tests, you can do 'python -m testtools.run tests'. To run specific tests,
# You can do 'python -m testtools.run -l tests'
# Set the env variable PARAMS_FILE to point to your ini file. Else it will try to pick params.ini in PWD
#
import os
import fixtures
import testtools
import time

from vn_test import *
from vm_test import *
from connections import ContrailConnections
from tcutils.wrappers import preposttest_wrapper
from testtools import skipIf
from neutron.base import BaseNeutronTest
import test
from tcutils.util import *
from floating_ip import FloatingIPFixture

class TestRouters(BaseNeutronTest):

    @classmethod
    def setUpClass(cls):
        super(TestRouters, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestRouters, cls).tearDownClass()


    @skipIf(os.environ.get('MX_GW_TEST') != '1',"Skiping Test. Env variable MX_GW_TEST is not set. Skiping the test")
    @preposttest_wrapper
    def test_basic_snat_behavior_with_config_and_vrouter_restart(self):
        vm1_name = get_random_name('vm_private')
        vn1_name = get_random_name('vn_private')
        vn1_subnets = [get_random_cidr()]
        self.allow_default_sg_to_allow_all_on_project(self.inputs.project_name)
        ext_vn_fixture = self.create_external_network(self.connections, self.inputs)
        ext_vn_fixture.verify_on_setup()
        vn1_fixture = self.create_vn(vn1_name, vn1_subnets)
        vn1_fixture.verify_on_setup()
        vm1_fixture = self.create_vm(vn1_fixture, vm1_name,
                                         image_name='ubuntu')
        vm1_fixture.verify_on_setup()

        router_name = get_random_name('router1')
        router_dict = self.create_router(router_name)
        router_rsp = self.quantum_fixture.router_gateway_set(
                router_dict['id'],
                ext_vn_fixture.vn_id)
        self.add_vn_to_router(router_dict['id'], vn1_fixture)
    
        assert self.verify_snat(vm1_fixture)

        for compute_ip in self.inputs.compute_ips:
            self.inputs.restart_service('contrail-vrouter', [compute_ip])

        for cfgm_ip in self.inputs.cfgm_ips:
            self.inputs.restart_service('contrail-api', [cfgm_ip])

        time.sleep(30)
        vm2_name = get_random_name('new_private_vm')
        vm2_fixture = self.create_vm(vn1_fixture, vm2_name,
                                         image_name='ubuntu')
        assert vm2_fixture.verify_on_setup()
        assert self.verify_snat(vm2_fixture)

    @skipIf(os.environ.get('MX_GW_TEST') != '1',"Skiping Test. Env variable MX_GW_TEST is not set. Skiping the test")
    @preposttest_wrapper
    def test_basic_snat_behavior_with_fip_and_config_and_vrouter_restart(self):
        vm1_name = get_random_name('vm_private')
        vm2_name = get_random_name('vm_public')
        vn1_name = get_random_name('vn_private')
        vn1_subnets = [get_random_cidr()]
        self.allow_default_sg_to_allow_all_on_project(self.inputs.project_name)
        ext_vn_fixture = self.create_external_network(self.connections, self.inputs) 
        ext_vn_fixture.verify_on_setup()
        vn1_fixture = self.create_vn(vn1_name, vn1_subnets)
        vn1_fixture.verify_on_setup()
        vm1_fixture = self.create_vm(vn1_fixture, vm1_name,
                                         image_name='ubuntu')
        vm1_fixture.verify_on_setup()
        vm2_fixture = self.create_vm(ext_vn_fixture, vm2_name,
                                         image_name='ubuntu')
        assert vm2_fixture.verify_on_setup()
       
        router_name = get_random_name('router1')
        router_dict = self.create_router(router_name)
        router_rsp = self.quantum_fixture.router_gateway_set(
                router_dict['id'],
                ext_vn_fixture.vn_id)
        self.add_vn_to_router(router_dict['id'], vn1_fixture)
        assert self.verify_snat(vm1_fixture)
        assert self.verify_snat_with_fip(ext_vn_fixture, vm2_fixture, vm1_fixture, connections= self.connections, inputs = self.inputs)
        for compute_ip in self.inputs.compute_ips:
            self.inputs.restart_service('contrail-vrouter', [compute_ip])

        for cfgm_ip in self.inputs.cfgm_ips:
            self.inputs.restart_service('contrail-api', [cfgm_ip])

        time.sleep(30)

        vm3_name = get_random_name('new_private_vm')
        vm3_fixture =  self.create_vm(vn1_fixture, vm3_name,
                                         image_name='ubuntu')

        assert vm3_fixture.verify_on_setup()
        assert self.verify_snat(vm3_fixture)
        assert self.verify_snat_with_fip(ext_vn_fixture, vm2_fixture, vm3_fixture, connections= self.connections, inputs = self.inputs)

    def verify_snat_with_fip(self, ext_vn_fixture, public_vm_fix, vm_fixture, connections, inputs):
        result = True
        fip_fixture = self.useFixture(
            FloatingIPFixture(
                project_name = inputs.project_name,
                inputs = inputs,
                connections = connections,
                pool_name='',
                vn_id=ext_vn_fixture.vn_id, option='neutron'))
        assert fip_fixture.verify_on_setup()
        fip_id = fip_fixture.create_and_assoc_fip(
                ext_vn_fixture.vn_id, vm_fixture.vm_id)
        self.addCleanup(fip_fixture.disassoc_and_delete_fip, fip_id)
        fip = vm_fixture.vnc_lib_h.floating_ip_read(
            id=fip_id).get_floating_ip_address()
        if not public_vm_fix.ping_to_ip(fip):
            result = result and False
            self.logger.error('Ping from %s to %s FAILED' %(public_vm_fix.vm_name, vm_fixture.vm_name))
        public_vm_fix.put_pub_key_to_vm()
        vm_fixture.put_pub_key_to_vm()
        self.logger.info("scp files from public_vm %s to private vm %s " %(public_vm_fix.vm_name, vm_fixture.vm_name))
        result = result and public_vm_fix.check_file_transfer(dest_vm_fixture=vm_fixture, mode='scp', size='1000', fip = fip)
        return result

