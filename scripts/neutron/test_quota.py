import random
from vn_test import MultipleVNFixture
from floating_ip import FloatingIPFixture
from common.connections import ContrailConnections
from tcutils.wrappers import preposttest_wrapper
from user_test import UserFixture
from project_test import ProjectFixture
from common.neutron.base import BaseNeutronTest
import test
from tcutils.util import *


class TestQuota(BaseNeutronTest):

    @classmethod
    def setUpClass(cls):
        super(TestQuota, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestQuota, cls).tearDownClass()

    @preposttest_wrapper
    def test_default_quota_for_admin_tenant(self):
        '''Test default quota for admin tenant
        '''
        result = True
        quota_dict = self.admin_connections.quantum_fixture.show_quota(
            self.admin_connections.project_id)
        for neutron_obj in quota_dict['quota']:
            if quota_dict['quota'][neutron_obj] != -1:
                self.logger.error(
                    "Default Quota limit not followed for %s and is set to %s " %
                    (neutron_obj, quota_dict['quota'][neutron_obj]))
                result = False
        assert result, 'Default quota for admin tenant is not set'

    @preposttest_wrapper
    def test_default_quota_for_new_tenant(self):
        result = True
        quota_dict = self.connections.quantum_fixture.show_quota(
            self.connections.project_id)
        for neutron_obj in quota_dict['quota']:
            if quota_dict['quota'][neutron_obj] != -1:
                self.logger.error(
                    "Default Quota limit not followed for %s and is set to %s " %
                    (neutron_obj, quota_dict['quota'][neutron_obj]))
                result = False
        assert result, 'Default quota for custom tenant is not set'

    @preposttest_wrapper
    def test_update_quota_for_new_tenant(self):
        '''Update quota for new custom tenent using neutron quota_update
        '''
        result = True
        quota_dict = {
            'subnet': 3,
            'router': 5,
            'network': 3,
            'floatingip': 4,
            'port': 5,
            'security_group': 4,
            'security_group_rule': 6}
        quota_rsp = self.connections.quantum_fixture.update_quota(
            self.connections.project_id,
            quota_dict)
        quota_show_dict = self.connections.quantum_fixture.show_quota(
            self.connections.project_id)

        for neutron_obj in quota_rsp['quota']:
            if quota_rsp['quota'][neutron_obj] != quota_show_dict[
                    'quota'][neutron_obj]:
                self.logger.error(
                    "Quota update unsuccessful for %s for admin tenant " %
                    (neutron_obj))
                result = False
        assert result, 'Failed to update quota for admin tenant'

    @preposttest_wrapper
    def test_quota_update_of_new_project_by_admin(self):
        '''Launch two custom tenants, quota update by admin tenant should be successful
           quota update of one custom tenant by other should fail
        '''
        result = True
        quota_dict = {
            'subnet': 3,
            'router': 5,
            'network': 3,
            'floatingip': 4,
            'port': 5,
            'security_group': 4,
            'security_group_rule': 6}

        project_name = get_random_name('project1')
        user_fixture = self.useFixture(UserFixture(
            connections=self.connections, username='test_usr',
            password='testusr123'))
        project_fixture_obj = self.useFixture(ProjectFixture(
            username=self.inputs.stack_user,
            password=self.inputs.stack_password,
            project_name=project_name,
            vnc_lib_h=self.vnc_lib,
            connections=self.connections))
        user_fixture.add_user_to_tenant(project_name, 'test_usr', 'Member')
        assert project_fixture_obj.verify_on_setup()
        proj_connection = project_fixture_obj.get_project_connections(
            'test_usr',
            'testusr123')

        project_name1 = get_random_name('project2')
        user_fixture1 = self.useFixture(UserFixture(
            connections=self.connections, username='test_usr1',
            password='testusr1231'))
        project_fixture_obj1 = self.useFixture(ProjectFixture(
            username='test1',
            password='test1231',
            project_name=project_name1,
            vnc_lib_h=self.vnc_lib,
            connections=self.connections))
        user_fixture1.add_user_to_tenant(project_name1, 'test_usr1', 'Member')
        assert project_fixture_obj1.verify_on_setup()

        quota_rsp = self.admin_connections.quantum_fixture.update_quota(
            project_fixture_obj1.project_id,
            quota_dict)
        quota_show_dict = self.admin_connections.quantum_fixture.show_quota(
            project_fixture_obj1.project_id)

        for neutron_obj in quota_rsp['quota']:
            if quota_rsp['quota'][neutron_obj] != quota_show_dict[
                    'quota'][neutron_obj]:
                self.logger.error(
                    "Quota update unsuccessful for %s for %s tenant " %
                    (neutron_obj, project_name1))
                result = False
        assert result, 'Quota update by admin tenant failed'
        result1 = proj_connection.quantum_fixture.update_quota(
            project_fixture_obj1.project_id,
            quota_dict)
        assert not result1, 'Quota update of %s by %s successful not expected' % (
            project_name1, project_name)

    @preposttest_wrapper
    def test_quota_update_of_specific_tenant(self):
        '''Quota update of one tenant should not affect
           quota for other tenant
        '''
        result = True
        quota_dict = {
            'subnet': 3,
            'router': 5,
            'network': 3,
            'floatingip': 4,
            'port': 5,
            'security_group': 4,
            'security_group_rule': 6}

        project_name = get_random_name('project1')
        user_fixture = self.useFixture(UserFixture(
            connections=self.connections, username='test_usr',
            password='testusr123'))
        project_fixture_obj = self.useFixture(ProjectFixture(
            username=self.inputs.stack_user,
            password=self.inputs.stack_password,
            project_name=project_name,
            vnc_lib_h=self.vnc_lib,
            connections=self.connections))
        user_fixture.add_user_to_tenant(project_name, 'test_usr', 'Member')
        assert project_fixture_obj.verify_on_setup()

        project_name1 = get_random_name('project2')
        user_fixture1 = self.useFixture(UserFixture(
            connections=self.connections, username='test_usr1',
            password='testusr1231'))
        project_fixture_obj1 = self.useFixture(ProjectFixture(
            username='test1',
            password='test1231',
            project_name=project_name1,
            vnc_lib_h=self.vnc_lib,
            connections=self.connections))
        user_fixture1.add_user_to_tenant(project_name1, 'test_usr1', 'Member')
        assert project_fixture_obj1.verify_on_setup()

        quota_show_dict1 = self.admin_connections.quantum_fixture.show_quota(
            project_fixture_obj.project_id)

        quota_rsp = self.admin_connections.quantum_fixture.update_quota(
            project_fixture_obj1.project_id,
            quota_dict)
        quota_show_dict = self.admin_connections.quantum_fixture.show_quota(
            project_fixture_obj1.project_id)

        for neutron_obj in quota_rsp['quota']:
            if quota_rsp['quota'][neutron_obj] != quota_show_dict[
                    'quota'][neutron_obj]:
                self.logger.error(
                    "Quota update unsuccessful for %s for %s tenant " %
                    (neutron_obj, project_name1))
                result = False
        assert result, 'Quota update by admin tenant failed'

        quota_show_dict2 = self.admin_connections.quantum_fixture.show_quota(
            project_fixture_obj.project_id)

        for neutron_obj in quota_show_dict2['quota']:
            if quota_show_dict2['quota'][neutron_obj] != quota_show_dict1[
                    'quota'][neutron_obj]:
                self.logger.error(
                    "Quota updated for %s for %s tenant not expected " %
                    (neutron_obj, project_name))
                result = False
        assert result, 'Quota update for %s by admin updated quota for %s also not expected' % (
            project_name1, project_name)

