import unittest
import networkx as nx
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import calc_functions
from classes import RadialPowerSystem


class CheckerFunctionTestCase(unittest.TestCase):


    def test_loop_check(self):
        """Test loop_check decorator for calc_flows_PU"""
        digraph = nx.DiGraph()
        digraph.add_edge("1", "2")
        digraph.add_edge("2", "3")
        digraph.add_edge("3", "1")
        self.assertRaises(Warning, calc_functions.calc_flows_PU, digraph)


    def test_length_check_zero(self):
        """Test length_check decorator for calc_flows_PU for zero edge length"""
        digraph = nx.DiGraph()
        digraph.add_edge("1", "2", length=0)
        self.assertRaises(ValueError, calc_functions.calc_flows_PU, digraph)


    def test_length_check_neg(self):
        """Test length_check decorator for calc_flows_PU for negative edge length"""
        digraph = nx.DiGraph()
        digraph.add_edge("1", "2", length=-1)
        self.assertRaises(ValueError, calc_functions.calc_flows_PU, digraph)


    def test_voltage_check_between_nodes(self):
        """Test voltage_check decorator for calc_flows_PU between connected nodes"""
        digraph = nx.DiGraph()
        digraph.add_node("1", nomVLL=240, nomVLN=120, phase=1, w=1, vAr=0, nodeType="load")
        digraph.add_node("2", nomVLL=600, nomVLN=480, phase=1, w=1, vAr=0, nodeType="load")
        digraph.add_edge("1", "2", length=1)
        self.assertRaises(ValueError, calc_functions.calc_flows_PU, digraph)


    def test_voltage_check_incompatible(self):
        """Test voltage_check decorator for calc_flows_PU to check for incorrect voltage inputs"""
        digraph = nx.DiGraph()
        digraph.add_node("1", nomVLL=1, nomVLN=1, phase=1, w=1, vAr=0, nodeType="load")
        digraph.add_node("2", nomVLL=1, nomVLN=1, phase=1, w=1, vAr=0, nodeType="load")
        digraph.add_edge("1", "2", length=1)
        self.assertRaises(ValueError, calc_functions.calc_flows_PU, digraph)


    def test_voltage_check_transformer(self):
        """Test oltage_check decorator for calc_flows_PU to check for incompatible transformer input voltage to node"""
        digraph = nx.DiGraph()
        digraph.add_node("1", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=7.5,
                         nomPrimaryV=480, nomSecondaryV1=999, nomSecondaryV2=999,
                         nodeType="transformer", primaryVoltage=480)
        digraph.add_node("2", nomVLL=240, nomVLN=120, phase=1, w=1, vAr=0, nodeType="load")
        digraph.add_edge("1", "2", length=1)
        self.assertRaises(ValueError, calc_functions.calc_flows_PU, digraph)


class SystemCalcsTestCase(unittest.TestCase):

    def test_simple_example_voltage(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, phase=1, sscXfmrSec=75000.0)
        G.add_node("2", nomVLL=480, phase=1, w=2000.0, vAr=0.0, nodeType="load")
        G.add_connection("1", "2", wireSize="1/0", conduitMat="PVC", length=1400.0)
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        self.assertGreater(G.node["1"]["trueVoltage"].real, G.node["2"]["trueVoltage"].real)


    def test_simple_example_SSC(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=75000.0)
        G.add_node("2", nomVLL=480, nomVLN=240, phase=1, w=2000.0, vAr=0.0, nodeType="load")
        G.add_connection("1", "2", wireSize="1/0", conduitMat="PVC", length=1400.0)
        calc_functions.per_unit_conv(G)
        calc_functions.calc_sym_ssc(G)
        self.assertGreater(G.node["1"]["SSC_LL"].real, G.node["2"]["SSC_LL"].real)
        self.assertGreater(G.node["1"]["SSC_LN"].real, G.node["2"]["SSC_LN"].real)


if __name__ == '__main__':
    unittest.main()
