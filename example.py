# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 07:56:31 2017

@author: AtotheM
"""
from calc_functions import *
from checker_functions import over_voltage_check
from plotting import *
import networkx as nx
from classes import RadialPowerSystem
import matplotlib.pyplot as plt


#########################################################################################
"""Model Graph for Testing"""
#########################################################################################

"""Notes:
- nomVoltage, nomSecondaryV, nomPrimaryV must be an int
- transformers must always have a nomSecondaryV2 and nomSecondaryV1... need to fix.
"""

G = RadialPowerSystem()

# G.add_node("service", nomVoltage=480, phase=1, nodeType="service")
# G.add_node("tap1", phase=1, nodeType="bus", nomVoltage=240)
# G.add_node("load1", nomVoltage=240, phase=1, vA=10000.0, vAr=1.0, nodeType="load")
# G.add_node("load2", nomVoltage=120, phase=1, vA=1000.0, vAr=1.0, nodeType="load")
# G.add_node("load3", nomVoltage=120, phase=1, vA=500.0, vAr=1.0, nodeType="load")
# G.add_node("tap2", phase=1, nodeType="bus", nomVoltage=120)
# G.add_node("load4", nomVoltage=120, phase=1, vA=500.0, vAr=1.0, nodeType="load")
#
# G.add_node("xfmr1", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=50.0,
#            nomPrimaryV = 480, nomSecondaryV1=120, nomSecondaryV2=240,
#            nodeType="transformer")
#
# G.add_connection("service", "xfmr1", wireSize=4, conduitMat="PVC", length=100.0)
# G.add_connection("xfmr1", "tap1", wireSize=4, conduitMat="PVC", length=200.0)
# G.add_connection("tap1", "load1", wireSize=4, conduitMat="PVC", length=200.0)
# G.add_connection("tap1", "load2", wireSize=4, conduitMat="PVC", length=200.0)
# G.add_connection("tap1", "load3", wireSize=4, conduitMat="PVC", length=200.0)
# G.add_connection("tap1", "tap2", wireSize=4, conduitMat="PVC", length=200.0)
# G.add_connection("tap2", "load4", wireSize=4, conduitMat="PVC", length=200.0)


G.add_node("service", nomVoltage=120, phase=1, nodeType="service")
G.add_node("load1", nomVoltage=120, phase=1, vA=1200.0, vAr=0.0, nodeType="load")
G.add_node("load2", nomVoltage=120, phase=1, vA=1200.0, vAr=0.0, nodeType="load")


G.add_connection("service", "load2", wireSize=400, conduitMat="steel", length=10000.0)
G.add_edge("service", "load1", xL=0.049, rL=0.035, length=10000.0)



#########################################################################################
"""Testing Calculations"""
#########################################################################################

#if __name__ == "__main__":
#    calc_flows(G)
#    calc_voltages(G)
#    over_voltage_check(G)
#    for i in G.nodes():
#        print i
#        print G.node[i]
#    for i in G.edges(data=True):
#        print i
#    nx.draw_networkx(G)
plot = True
if __name__ == "__main__":
    calc_flows(G)
    per_unit_conv(G)
    calc_flows_PU(G)
    calc_voltages_PU(G)
    actual_conv(G)
    if plot:
        draw_graph_labels(G)
