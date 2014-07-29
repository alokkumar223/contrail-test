################################################################################
class sdn_4vn_xvm_config ():
    def __init__(self, domain= 'default-domain', project= 'admin', compute_node_list= None, username= None, password= None):
	print "building dynamic topo"
        ##
        # Domain and project defaults: Do not change until support for non-default is tested!
        self.domain= domain; self.project= project; self.username= username; self.password= password
        ##
        # Define VN's in the project:
        self.vnet_list=  ['vnet1','vnet2', 'vnet3', 'vnet4']
        ##
        # Define network info for each VN:
        self.vn_nets=  {'vnet1': ['10.1.1.0/24', '11.1.1.0/24'], 'vnet2': ['10.1.2.0/24', '11.1.2.0/24'], 'vnet3': ['10.1.3.0/24', '11.1.3.0/24'], 'vnet4': ['10.1.4.0/24', '11.1.4.0/24']}
        ##
        # Define network policies
        self.policy_list=  ['policy0', 'policy1', 'policy100']
        self.vn_policy=  {'vnet1': ['policy0'], 'vnet2': ['policy0'],'vnet3':['policy0'],'vnet4':['policy0']}

        self.vn_of_vm= {'vm1': 'vnet1', 'vm2': 'vnet1', 'vm3': 'vnet1', 'vm4': 'vnet2', 'vm5': 'vnet2',
                        'vm6': 'vnet3', 'vm7': 'vnet3', 'vm8': 'vnet3', 'vm9': 'vnet4', 'vm10': 'vnet4','vm11':'vnet4','vm12':'vnet3'}

        #Define the vm to compute node mapping to pin a vm to a particular
        #compute node or else leave empty.
        self.vm_node_map = {}
        if compute_node_list is not None:
            if len(compute_node_list) == 2:
                self.vm_node_map = {'vm1':'CN0', 'vm2':'CN0', 'vm3':'CN1', 'vm4':'CN0', 'vm5':'CN1',
                                    'vm6':'CN0', 'vm7':'CN0', 'vm8':'CN1', 'vm9':'CN0', 'vm10':'CN1','vm11':'CN0','vm12':'CN1'}
            elif len(compute_node_list) > 2:
               self.vm_node_map = {'vm1':'CN0', 'vm2':'CN0', 'vm3':'CN2', 'vm4':'CN0', 'vm5':'CN1', 'vm6':'CN0',
                                   'vm7':'CN0', 'vm8':'CN2', 'vm9':'CN0', 'vm10':'CN1', 'vm11':'CN0','vm12':'CN1'}

        #Logic to create a vm to Compute node mapping.
        if self.vm_node_map:
            CN = []
            for cn in self.vm_node_map.keys():
                if self.vm_node_map[cn] not in CN:
                    CN.append(self.vm_node_map[cn])
            my_node_dict = {}
            if compute_node_list is not None:
                if len(compute_node_list) >= len(CN):
                    my_node_dict = dict(zip(CN, compute_node_list))

            if my_node_dict:
                for key in my_node_dict:
                    for key1 in self.vm_node_map:
                        if self.vm_node_map[key1] == key:
                            self.vm_node_map[key1] = my_node_dict[key]

        ##
        # Define network policy rules
        self.rules= {}
        # Multiple policies are defined with different action for the test traffic streams..
        self.policy_test_order= ['policy0', 'policy1', 'policy0']
        self.rules['policy0']= [
            {'direction': '<>', 'protocol': 'any', 'dest_network': 'any', 'source_network': 'any', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'}]
        self.rules['policy1']= [
            {'direction': '<>', 'protocol': 'udp', 'dest_network': 'vnet1', 'source_network': 'vnet0', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'},
            {'direction': '<>', 'protocol': 'udp', 'dest_network': 'vnet2', 'source_network': 'vnet0', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'}]
        self.rules['policy100']= [
            {'direction': '<>', 'protocol': 'udp', 'dest_network': 'any', 'source_network': 'any', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'}]

        #Define the security_group and its rules
        # Define security_group name
        self.sg_list=['sg_allow_all', 'sg_allow_tcp', 'sg_allow_udp', 'sg_allow_icmp', 'sg_allow_udp_sg']
        self.sg_names = self.sg_list[:]
        ##
        #Define security_group with vm
        self.sg_of_vm = {}
        for key in self.vn_of_vm:
           self.sg_of_vm[key] = []
        self.sg_of_vm['vm6'] = [self.sg_list[4]]; self.sg_of_vm['vm9'] = [self.sg_list[4]]; self.sg_of_vm['vm10'] = [self.sg_list[4]];
        self.sg_of_vm['vm11'] = [self.sg_list[4]]; self.sg_of_vm['vm12'] = [self.sg_list[4]];
        ##Define the security group rules
        import uuid
        uuid_1= uuid.uuid1().urn.split(':')[2]
        uuid_2= uuid.uuid1().urn.split(':')[2]
        self.sg_rules={}
        for sg in self.sg_list:
            self.sg_rules[sg] = []
        self.sg_rules[self.sg_list[2]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'dst_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}],
                 'rule_uuid': uuid_1
               },{'direction' : '>',
                 'protocol' : 'any',
                 'src_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'dst_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}],'rule_uuid': uuid_2}]

        self.sg_rules[self.sg_list[4]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'dst_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_addresses': [{'security_group': self.domain + ':'+ self.project+ ':'+ self.sg_list[4]}],
                 'rule_uuid': uuid_1
               },{'direction' : '>',
                 'protocol' : 'any',
                 'src_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'dst_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}],'rule_uuid': uuid_2}]

        ##
        # Define traffic profile.
        self.traffic_profile= [{'src_vm':'vm1', 'dst_vm':'vm2', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},# intra VN, intra compute, same default SG
                               {'src_vm':'vm1', 'dst_vm':'vm3', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},# intra VN, inter compute, same default SG
                               {'src_vm':'vm1', 'dst_vm':'vm5', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},# inter VN, inter compute, same default SG
                               {'src_vm':'vm1', 'dst_vm':'vm4', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},# inter VN, intra compute, same default SG
                               {'src_vm':'vm6', 'dst_vm':'vm7', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},# intra VN, intra compute, diff. SG
                               {'src_vm':'vm6', 'dst_vm':'vm8', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},# intra VN, inter compute, diff. SG
                               {'src_vm':'vm6', 'dst_vm':'vm5', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},# inter VN, inter compute, diff. SG
                               {'src_vm':'vm6', 'dst_vm':'vm4', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},# inter VN, intra compute, diff. SG
                               {'src_vm':'vm9', 'dst_vm':'vm11','proto':'udp','sport':8000,'dport':9000,'exp':'pass'},# intra VN, intra compute, same non-default SG
                               {'src_vm':'vm9', 'dst_vm':'vm10','proto':'udp','sport':8000,'dport':9000,'exp':'pass'},# intra VN, inter compute, same non-default SG
                               {'src_vm':'vm9', 'dst_vm':'vm12','proto':'udp','sport':8000,'dport':9000,'exp':'pass'},# inter VN, inter compute, same non-default SG
                               {'src_vm':'vm9', 'dst_vm':'vm6', 'proto':'udp','sport':8000,'dport':9000,'exp':'pass'}]# inter VN, intra compute, same non-default SG

        # end __init__ 
# end class sdn_4vn_xvm_config

################################################################################
class sdn_topo_config ():
    def build_topo_sg_stateful(self, domain= 'default-domain', project= 'admin', compute_node_list= None, username= None, password= None):
        print "building dynamic topo"
        ##
        # Domain and project defaults: Do not change until support for non-default is tested!
        self.domain= domain; self.project= project; self.username= username; self.password= password
        ##
        # Define VN's in the project:
        self.vnet_list=  ['vnet1','vnet2']
        ##
        # Define network info for each VN:
        self.vn_nets=  {'vnet1': ['10.1.1.0/24', '11.1.1.0/24'], 'vnet2': ['10.1.2.0/24', '11.1.2.0/24']}
        ##
        # Define network policies
        self.policy_list=  ['policy0']
        self.vn_policy=  {'vnet1': ['policy0'], 'vnet2': ['policy0']}

        self.vn_of_vm= {'vm1': 'vnet1', 'vm2': 'vnet1', 'vm3': 'vnet2', 'vm4': 'vnet2'}

        #Define the vm to compute node mapping to pin a vm to a particular
        #compute node or else leave empty.
        self.vm_node_map = {}

        ##
        # Define network policy rules
        self.rules= {}
        # Multiple policies are defined with different action for the test traffic streams..
        self.policy_test_order= ['policy0']
        self.rules['policy0']= [
            {'direction': '<>', 'protocol': 'any', 'dest_network': 'any', 'source_network': 'any', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'}]

        #Define the security_group and its rules
        # Define security_group name
        self.sg_list=['sg1_ingress', 'sg2_ingress', 'sg1_egress', 'sg2_egress']
        self.sg_names = self.sg_list[:]
        ##
        #Define security_group with vm
        self.sg_of_vm = {}
        for key in self.vn_of_vm:
           self.sg_of_vm[key] = []
        self.sg_of_vm['vm1'] = [self.sg_list[0]]; self.sg_of_vm['vm2'] = [self.sg_list[2]]; self.sg_of_vm['vm3'] = [self.sg_list[1]];
        self.sg_of_vm['vm4'] = [self.sg_list[3]];
        ##Define the security group rules
        '''import uuid
        uuid_1= uuid.uuid1().urn.split(':')[2]
        uuid_2= uuid.uuid1().urn.split(':')[2]'''
        self.sg_rules={}
        for sg in self.sg_list:
            self.sg_rules[sg] = []
        self.sg_rules[self.sg_list[0]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'dst_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]}]

        self.sg_rules[self.sg_list[1]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'dst_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]}]

        self.sg_rules[self.sg_list[2]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'src_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'dst_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]}]

        self.sg_rules[self.sg_list[3]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'src_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'dst_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]}]


        ##
        # Define traffic profile.
        self.traffic_profile= [{'src_vm':'vm1', 'dst_vm':'vm2', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},
                               {'src_vm':'vm2', 'dst_vm':'vm1', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},
    			       {'src_vm':'vm1', 'dst_vm':'vm3', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},
                               {'src_vm':'vm3', 'dst_vm':'vm1', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},
                               {'src_vm':'vm1', 'dst_vm':'vm4', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},
                               {'src_vm':'vm4', 'dst_vm':'vm1', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},
                               {'src_vm':'vm2', 'dst_vm':'vm4', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'},
                               {'src_vm':'vm4', 'dst_vm':'vm2', 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'}
			      ]

        # end build_topo_sg_stateful
# end class sdn_topo_config
################################################################################

class sdn_topo_config_multiproject():

    def __init__(self, domain='default-domain'):
        print "building dynamic topo"
        self.project_list = ['project1', 'project2']
	self.topo_of_project = {self.project_list[0]:'build_topo1',self.project_list[1]:'build_topo1'}

        ##
        # Define traffic profile.
        self.traffic_profile= [{'src_vm':['project1','vm1'], 'dst_vm':['project2','vm1'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'},
                               {'src_vm':['project1','vm2'], 'dst_vm':['project2','vm2'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'}
                               {'src_vm':['project1','vm1'], 'dst_vm':['project2','vm2'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'}
                               {'src_vm':['project1','vm2'], 'dst_vm':['project2','vm1'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'}
                               {'src_vm':['project2','vm1'], 'dst_vm':['project1','vm1'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'}
                               {'src_vm':['project2','vm2'], 'dst_vm':['project1','vm2'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'}
                               {'src_vm':['project2','vm2'], 'dst_vm':['project1','vm1'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'pass'}
                               {'src_vm':['project2','vm1'], 'dst_vm':['project1','vm2'], 'proto':'udp', 'sport':8000, 'dport':9000, 'exp':'fail'}
                              ]

    
    def build_topo1(self, domain= 'default-domain', project= 'admin', username= None, password= None):
        ##
        # Domain and project defaults: Do not change until support for non-default is tested!
        self.domain= domain; self.project= project; self.username= username; self.password= password
        ##
        # Define VN's in the project:
        self.vnet_list=  ['vnet1','vnet2']
        ##
        # Define network info for each VN:
        self.vn_nets=  {'vnet1': ['10.1.1.0/24', '11.1.1.0/24'], 'vnet2': ['10.1.2.0/24', '11.1.2.0/24']}
        ##
        # Define network policies
        self.policy_list=  ['policy0']
        self.vn_policy=  {'vnet1': ['policy0'], 'vnet2': ['policy0']}

        self.vn_of_vm= {'vm1': 'vnet1', 'vm2': 'vnet1', 'vm3': 'vnet2', 'vm4': 'vnet2'}

        #Define the vm to compute node mapping to pin a vm to a particular
        #compute node or else leave empty.
        self.vm_node_map = {}

        ##
        # Define network policy rules
        self.rules= {}
        # Multiple policies are defined with different action for the test traffic streams..
        self.policy_test_order= ['policy0']
        self.rules['policy0']= [
            {'direction': '<>', 'protocol': 'any', 'dest_network': 'any', 'source_network': 'any', 'dst_ports': 'any', 'simple_action': 'pass', 'src_ports': 'any'}]

        #Define the security_group and its rules
        # Define security_group name
        self.sg_list=['sg1']
        self.sg_names = self.sg_list[:]
        ##
        #Define security_group with vm
        self.sg_of_vm = {}
        for key in self.vn_of_vm:
           self.sg_of_vm[key] = []
        self.sg_of_vm['vm1'] = [self.sg_list[0]]; self.sg_of_vm['vm3'] = [self.sg_list[0]];
        ##Define the security group rules
        self.sg_rules={}
        for sg in self.sg_list:
            self.sg_rules[sg] = []
        self.sg_rules[self.sg_list[0]]=[
               {'direction' : '>',
                 'protocol' : 'udp',
                 'dst_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]},
               {'direction' : '>',
                 'protocol' : 'udp',
                 'src_addresses': [{'security_group': 'local', 'subnet' : None}],
                 'dst_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'src_ports': [{'start_port' : 0, 'end_port' : 65535}],
                 'dst_addresses': [{'subnet' : {'ip_prefix' : '0.0.0.0', 'ip_prefix_len' : 0}}]}]

        # end build_topo1 
# end class sdn_topo_config_multiproject 
################################################################################

