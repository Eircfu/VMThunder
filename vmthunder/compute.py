#!/usr/bin/env python
import threading
import thread
import time

from vmthunder.drivers import fcg
from vmthunder.session import Session
from vmthunder.instance import Instance
from vmthunder.singleton import SingleTon
from vmthunder.openstack.common import log as logging
from vmthunder.drivers import volt


LOG = logging.getLogger(__name__)

@SingleTon
class Compute():
    def __init__(self):
        self.session_dict = {}
        self.instance_dict = {}
        self.cache_group = fcg.create_group()
        LOG.debug("creating a Compute_node")
        

    def heartbeat(self):
        info = volt.heartbeat()
        for session in info:
            for each_key in self.instance_dict:
                if self.session_dict[each_key].peer_id == session['peer_id']:
                    self.session_dict[each_key].adjust_for_heartbeat(session['parents'])
                    break
    

    def destroy(self, vm_name):
        if self.instance_dict.has_key(vm_name):
            instance = self.instance_dict[vm_name]
            session = self.session_dict[instance.volume_name]
            instance.del_vm()
            session.destroy(vm_name)
            del self.instance_dict[vm_name]

    def list(self):
        def build_list_object(instances):
            instance_list = []
            for instance in instances.keys():
                instance_list.append({
                    'vm_name': instances[instance].vm_name,
                })
            return dict(instances=instance_list)

        return build_list_object(self.instance_dict)

    def create(self, volume_name, vm_name, connections, snapshot_dev):
        if vm_name not in self.instance_dict.keys():
            LOG.debug("in compute to execute the method create")
            if not self.session_dict.has_key(volume_name):
                self.session_dict[volume_name] = Session(volume_name)
            session = self.session_dict[volume_name]
            origin_path = session.deploy_image(vm_name, connections)
            self.instance_dict[vm_name] = Instance.factory(volume_name, vm_name, snapshot_dev)
            LOG.debug("origin is %s" % origin_path)
            self.instance_dict[vm_name].start_vm(origin_path)
            return self.instance_dict[vm_name].snapshot_path

    def adjust_structure(self, volume_name, delete_connections, add_connections):
        if self.session_dict.has_key(volume_name):
            session = self.session_dict[volume_name]
            session.adjust_structure(delete_connections, add_connections)

