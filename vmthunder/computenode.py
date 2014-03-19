#!/usr/bin/env python

from pydm.dmsetup import Dmsetup
from vmthunder.session import Session
from vmthunder.instancecommon import InstanceCommon
from vmthunder.instancesnapcache import InstanceSnapCache

class ComputeNode():
    
    
    #TODO realize singleton pattern

    def __init__(self):
        #TODO initial fcg
        self.session_dict = {}
        self.instance_dict = {}
        
    def delete_vm(self, vm_name, connections):
        instance = self.instance_dict[vm_name]
        session = self.session_dict[instance.image_id]
        instance.del_vm()
        session.destroy(vm_name, connections)

    def star_vm(self, image_id, vm_name, connections, snapshot_dev):
        if(not self.session_dict.has_key(image_id)):
            self.session_dict[image_id] = Session('fcg', image_id)
        session = self.session_dict[image_id]
        origin_path = session.deploy_image(vm_name, connections)
        self.instance_dict[vm_name] = InstanceCommon('fcg', image_id, vm_name, snapshot_dev)
        self.instance_dict[vm_name].star_vm(origin_path)
        
    def adjust_structure(self, image_id, delete_connections, add_connections):
        session = self.session_dict[image_id]
        session.adjust_structure(delete_connections, add_connections)
