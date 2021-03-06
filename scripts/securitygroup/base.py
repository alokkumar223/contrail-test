import test
from vn_test import MultipleVNFixture
from vm_test import MultipleVMFixture
from fabric.api import run, hide, settings
from vn_test import VNFixture
from vm_test import VMFixture
from policy_test import PolicyFixture
from common.policy.config import ConfigPolicy
from security_group import SecurityGroupFixture, get_secgrp_id_from_name
from common import isolated_creds
from tcutils.util import get_random_name

class BaseSGTest(test.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseSGTest, cls).setUpClass()
        cls.isolated_creds = isolated_creds.IsolatedCreds(cls.__name__, \
                                cls.inputs, ini_file = cls.ini_file, \
                                logger = cls.logger)
        cls.isolated_creds.setUp()
        cls.project = cls.isolated_creds.create_tenant()
        cls.isolated_creds.create_and_attach_user_to_tenant()
        cls.inputs = cls.isolated_creds.get_inputs()
        cls.connections = cls.isolated_creds.get_conections()
        cls.quantum_fixture= cls.connections.quantum_fixture
        cls.nova_fixture = cls.connections.nova_fixture
        cls.vnc_lib= cls.connections.vnc_lib
        cls.agent_inspect= cls.connections.agent_inspect
        cls.cn_inspect= cls.connections.cn_inspect
        cls.analytics_obj=cls.connections.analytics_obj

    #end setUpClass

    @classmethod
    def tearDownClass(cls):
	cls.isolated_creds.delete_user()
        cls.isolated_creds.delete_tenant()
        super(BaseSGTest, cls).tearDownClass()
    #end tearDownClass

    def setUp(self):
        super(BaseSGTest, self).setUp()

    def tearDown(self):
        super(BaseSGTest, self).tearDown()

    def create_sg_test_resources(self):
        """Config common resources."""
	self.logger.info("Configuring setup for security group tests.")

        vn_s = {'vn1': '20.1.1.0/24', 'vn2': ['10.1.1.0/24']}
        self.multi_vn_fixture = self.useFixture(MultipleVNFixture(
            connections=self.connections, inputs=self.inputs, subnet_count=2,
            vn_name_net=vn_s,  project_name=self.inputs.project_name))
        vns = self.multi_vn_fixture.get_all_fixture_obj()
        (self.vn1_name, self.vn1_fix) = self.multi_vn_fixture._vn_fixtures[0]
        (self.vn2_name, self.vn2_fix) = self.multi_vn_fixture._vn_fixtures[1]

        self.logger.info("Configure security groups required for test.")
        self.config_sec_groups()

        self.multi_vm_fixture = self.useFixture(MultipleVMFixture(
            project_name=self.inputs.project_name, connections=self.connections,
            vm_count_per_vn=3, vn_objs=vns, image_name='ubuntu-traffic',
            flavor='contrail_flavor_small'))
        vms = self.multi_vm_fixture.get_all_fixture()
        (self.vm1_name, self.vm1_fix) = vms[0]
        (self.vm2_name, self.vm2_fix) = vms[1]
        (self.vm3_name, self.vm3_fix) = vms[2]
        (self.vm4_name, self.vm4_fix) = vms[3]
        (self.vm5_name, self.vm5_fix) = vms[4]
        (self.vm6_name, self.vm6_fix) = vms[5]

        self.logger.info("Verifying setup of security group tests.")
        self.verify_sg_test_resources()

        self.logger.info("Adding the sec groups to the VM's")
        self.vm1_fix.add_security_group(secgrp=self.sg1_name)
        self.vm1_fix.add_security_group(secgrp=self.sg2_name)
        self.vm2_fix.add_security_group(secgrp=self.sg2_name)
        self.vm4_fix.add_security_group(secgrp=self.sg1_name)
        self.vm4_fix.add_security_group(secgrp=self.sg2_name)
        self.vm5_fix.add_security_group(secgrp=self.sg1_name)

        self.logger.info("Remove the default sec group form the VM's")
	default_secgrp_id = get_secgrp_id_from_name(
                        	self.connections,
                        	':'.join([self.inputs.domain_name,
					self.inputs.project_name,
					'default']))
        self.vm1_fix.remove_security_group(secgrp=default_secgrp_id)
        self.vm2_fix.remove_security_group(secgrp=default_secgrp_id)
        self.vm4_fix.remove_security_group(secgrp=default_secgrp_id)
        self.vm5_fix.remove_security_group(secgrp=default_secgrp_id)

        self.logger.info(
            "Finished configuring setup for security group tests.")


    def config_sec_groups(self):
        self.sg1_name = 'test_tcp_sec_group' + '_' + get_random_name()
        rule = [{'direction': '<>',
                'protocol': 'tcp',
                 'dst_addresses': [{'subnet': {'ip_prefix': '10.1.1.0', 'ip_prefix_len': 24}},
                                   {'subnet': {'ip_prefix': '20.1.1.0', 'ip_prefix_len': 24}}],
                 'dst_ports': [{'start_port': 0, 'end_port': -1}],
                 'src_ports': [{'start_port': 0, 'end_port': -1}],
                 'src_addresses': [{'security_group': 'local'}],
                 },
                {'direction': '<>',
                 'protocol': 'tcp',
                 'src_addresses': [{'subnet': {'ip_prefix': '10.1.1.0', 'ip_prefix_len': 24}},
                                   {'subnet': {'ip_prefix': '20.1.1.0', 'ip_prefix_len': 24}}],
                 'src_ports': [{'start_port': 0, 'end_port': -1}],
                 'dst_ports': [{'start_port': 0, 'end_port': -1}],
                 'dst_addresses': [{'security_group': 'local'}],
                 }]

        self.sg1_fix = self.config_sec_group(name=self.sg1_name, entries=rule)

        self.sg2_name = 'test_udp_sec_group' + '_' + get_random_name()
        rule = [{'direction': '<>',
                'protocol': 'udp',
                 'dst_addresses': [{'subnet': {'ip_prefix': '10.1.1.0', 'ip_prefix_len': 24}},
                                   {'subnet': {'ip_prefix': '20.1.1.0', 'ip_prefix_len': 24}}],
                 'dst_ports': [{'start_port': 0, 'end_port': -1}],
                 'src_ports': [{'start_port': 0, 'end_port': -1}],
                 'src_addresses': [{'security_group': 'local'}],
                 },
                {'direction': '<>',
                 'protocol': 'udp',
                 'src_addresses': [{'subnet': {'ip_prefix': '10.1.1.0', 'ip_prefix_len': 24}},
                                   {'subnet': {'ip_prefix': '20.1.1.0', 'ip_prefix_len': 24}}],
                 'src_ports': [{'start_port': 0, 'end_port': -1}],
                 'dst_ports': [{'start_port': 0, 'end_port': -1}],
                 'dst_addresses': [{'security_group': 'local'}],
                 }]
        self.sg2_fix = self.config_sec_group(name=self.sg2_name, entries=rule)

    def verify_sg_test_resources(self):
        """verfiy common resources."""
        self.logger.debug("Verify the configured VN's.")
        assert self.multi_vn_fixture.verify_on_setup()

        self.logger.debug("Verify the configured VM's.")
        assert self.multi_vm_fixture.verify_on_setup()

        '''self.logger.info("Installing traffic package in VM.")
        self.vm1_fix.install_pkg("Traffic")
        self.vm2_fix.install_pkg("Traffic")
        self.vm3_fix.install_pkg("Traffic")
        self.vm4_fix.install_pkg("Traffic")
        self.vm5_fix.install_pkg("Traffic")
        self.vm6_fix.install_pkg("Traffic")'''

        self.logger.debug("Verify the configured security groups.")
        result, msg = self.sg1_fix.verify_on_setup()
        assert result, msg
        result, msg = self.sg2_fix.verify_on_setup()
        assert result, msg

        self.logger.debug("Verify the attached security groups in the VM.")
        result, msg = self.vm1_fix.verify_security_group(self.sg1_name)
        assert result, msg
        result, msg = self.vm1_fix.verify_security_group(self.sg2_name)
        assert result, msg
        result, msg = self.vm2_fix.verify_security_group(self.sg2_name)
        assert result, msg
        result, msg = self.vm4_fix.verify_security_group(self.sg1_name)
        assert result, msg
        result, msg = self.vm4_fix.verify_security_group(self.sg2_name)
        assert result, msg
        result, msg = self.vm5_fix.verify_security_group(self.sg2_name)
        assert result, msg

    def config_sec_group(self, name, secgrpid=None, entries=None):
        secgrp_fixture = self.useFixture(SecurityGroupFixture(self.inputs,
                                                              self.connections, self.inputs.domain_name, self.inputs.project_name,
                                                              secgrp_name=name, secgrp_id=secgrpid, secgrp_entries=entries,option=self.option))
        result, msg = secgrp_fixture.verify_on_setup()
        assert result, msg
        return secgrp_fixture

    def delete_sec_group(self, secgrp_fix):
        secgrp_fix.cleanUp()
        self.remove_from_cleanups(secgrp_fix)

    def remove_from_cleanups(self, fix):
        for cleanup in self._cleanups:
            if fix.cleanUp in cleanup:
                self._cleanups.remove(cleanup)
                break

    def config_policy_and_attach_to_vn(self, rules):
	randomname = get_random_name()
	policy_name = "sec_grp_policy_" + randomname
        policy_fix = self.config_policy(policy_name, rules)
        assert policy_fix.verify_on_setup()
        policy_vn1_attach_fix = self.attach_policy_to_vn(
            policy_fix, self.vn1_fix)
        policy_vn2_attach_fix = self.attach_policy_to_vn(
            policy_fix, self.vn2_fix)


#end class BaseSGTest

