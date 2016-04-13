import unittest
import sys
import os

sys.path.insert(0, os.path.abspath('.') + '/ofp/v0x01')

from controller2switch import flow_mod


class TestFlowMod(unittest.TestCase):

    def test_get_size(self):
        flow_mod_message = flow_mod.FlowMod(1, 300, 6000, 1, 1, 80, 0, 1)
        self.assertEqual(flow_mod_message.get_size(), 72)

    def test_pack(self):
        flow_mod_message = flow_mod.FlowMod(1, 300, 6000, 1, 1, 80, 0, 1)
        flow_mod_message.pack()

    def test_unpack(self):
        pass

sys.path.remove(os.path.abspath('.') + '/ofp/v0x01')
