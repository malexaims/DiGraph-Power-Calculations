import unittest
import networkx as nx
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import calc_functions
from classes import RadialPowerSystem

#TODO: Test that vdrop accross transformer is less than the base turns ratio

#TODO: Test that the ssc on secondary of XFMR is always less than the base turns ratio


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


#TODO: Test that the ssc on secondary of XFMR is always less than the base turns ratio

class TransformerTestCase(unittest.TestCase):

    def test_transformer_vdrop_single_phase_resistance(self):
        G = RadialPowerSystem("1")
        digraph = nx.DiGraph()
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=5.0, pctX=0.0, tapSetting=0.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=100.0)
        turnsRatio = G.node["2"]["nomPrimaryV"] / G.node["2"]["nomSecondaryV2"]
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        self.assertGreater(G.node["2"]["primaryVoltage"].real, G.node["2"]["secondaryVoltage2"].real * turnsRatio)


    def test_transformer_vdrop_single_phase_reactance(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=0.0, pctX=5.0, tapSetting=0.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=100.0)
        turnsRatio = G.node["2"]["nomPrimaryV"] / G.node["2"]["nomSecondaryV2"]
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        self.assertGreater(G.node["2"]["primaryVoltage"].real, G.node["2"]["secondaryVoltage2"].real * turnsRatio)


    def test_transformer_vdrop_single_phase_impedance(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=0.0, pctX=5.0, tapSetting=0.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=100.0)
        turnsRatio = G.node["2"]["nomPrimaryV"] / G.node["2"]["nomSecondaryV2"]
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        self.assertGreater(G.node["2"]["primaryVoltage"].real, G.node["2"]["secondaryVoltage2"].real * turnsRatio)


    def test_transformer_ssc_single_phase_impedance(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=1.0, pctX=1.0, tapSetting=0.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=0.00001)
        turnsRatio = G.node["2"]["nomPrimaryV"] / G.node["2"]["nomSecondaryV2"]
        calc_functions.per_unit_conv(G)
        calc_functions.calc_sym_ssc(G)
        self.assertGreater(G.node["2"]["SSC_LL"].real * turnsRatio, G.node["3"]["SSC_LL"].real)


    def test_transformer_FCBN_tap_single_phase_impedance(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=1.0, pctX=1.0, tapSetting=-5.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=0.00001)
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        turnsRatio = ((G.node["2"]["nomPrimaryV"] - (G.node["2"]["nomPrimaryV"].real * G.node["2"]["tapSetting"]/100.0))
                        / G.node["2"]["nomSecondaryV2"])
        self.assertLess(G.node["2"]["primaryVoltage"].real, G.node["2"]["secondaryVoltage2"].real * turnsRatio)

    def test_transformer_FCAN_tap_single_phase_impedance(self):
        G = RadialPowerSystem("1")
        G.add_node("1", nodeType="service", nomVLL=480, nomVLN=240, phase=1, sscXfmrSec=100000.0)
        G.add_node("2", phase=1, pctR=1.0, pctX=1.0, tapSetting=5.0, rating=10.0,
                         nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
                         nodeType="transformer")
        G.add_node("3", nomVLL=240, nomVLN=120, phase=1, w=10000.0, vAr=1000.0, nodeType="load")
        G.add_connection("1", "2", wireSize="400", conduitMat="PVC", length=100.0)
        G.add_connection("2", "3", wireSize="400", conduitMat="PVC", length=0.00001)
        calc_functions.per_unit_conv(G)
        calc_functions.calc_flows_PU(G)
        calc_functions.calc_voltages_PU(G)
        calc_functions.actual_conv(G)
        turnsRatio = ((G.node["2"]["nomPrimaryV"] - (G.node["2"]["nomPrimaryV"].real * G.node["2"]["tapSetting"]/100.0))
                        / G.node["2"]["nomSecondaryV2"])
        self.assertGreater(G.node["2"]["primaryVoltage"].real, G.node["2"]["secondaryVoltage2"].real * turnsRatio)



if __name__ == '__main__':
    unittest.main()
