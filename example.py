# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 07:56:31 2017

@author: AtotheM
"""
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from calc_functions import *
from checker_functions import over_voltage_check
from plotting import *
import networkx as nx
from classes import RadialPowerSystem
from report.reports import create_report
import matplotlib.pyplot as plt


#########################################################################################
"""Input Radial Power System Data Below"""
#########################################################################################

"""Instruction and usage notes:
- nomVoltage, nomSecondaryV, nomPrimaryV must be an integer.
- If the program is not working, and messages are not desribing the problem clearly, check inputs to make source
  there are no isolated nodes.
- Must instantiate a RadialPowerSystem object, then enter nodes and edges between the nodes for the program to function.
- Transformer tap settings are entered as float representations of percentages: 5% FCBN entered as -5.0, 5% FCAN entered as 5.0.
- Transformer ratings are entered in KVA.
- Transformer pctX and pctR are entered as float representations of percentages: 5% X entered as 5.0, 5% R entered as 5.0.
"""

G = RadialPowerSystem("Service #1")

G.add_node("service_xfmr", nodeType="service", nomVLL=480, nomVLN=240, phase=1, availSSC=75000, xRRatio=10.0)
G.add_node("DS5", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_connection("service_xfmr", "DS5", wireSize="1/0", conduitMat="PVC", length=35.0)


G.add_node("PB1", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("DS1_A", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("XFMR1", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=7.5,
           nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
           nodeType="transformer")
G.add_node("PNL_A", phase=1, nodeType="bus", nomVLL=240, nomVLN=120)
G.add_node("CCTV_1", nomVLL=240, phase=1, w=721.0, vAr=0.0, nodeType="load")
G.add_node("MVDS_1", nomVLN=120, phase=1, w=10.0, vAr=0.0, nodeType="load")
G.add_connection("DS5", "PB1", wireSize="1/0", conduitMat="PVC", length=10.0)
G.add_connection("PB1", "DS1_A", wireSize="1/0", conduitMat="PVC", length=10.0)
G.add_connection("DS1_A", "XFMR1", wireSize="1/0", conduitMat="steel", length=5.0)
G.add_connection("XFMR1", "PNL_A", wireSize=6, conduitMat="steel", length=5.0)
G.add_connection("PNL_A", "CCTV_1", wireSize=6, conduitMat="PVC", length=65.0)
G.add_connection("PNL_A", "MVDS_1", wireSize=6, conduitMat="PVC", length=65.0)


G.add_node("PB2", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("DS3_A", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("XFMR2", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=15.0,
           nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
           nodeType="transformer")
G.add_node("PNL_B", phase=1, nodeType="bus", nomVLL=240, nomVLN=120)
G.add_node("DMS_1", nomVLL=240, phase=1, w=7000.0, vAr=7000.0, nodeType="load")
G.add_node("MCCTV_1", nomVLN=120, phase=1, w=104.0, vAr=0.0, nodeType="load")
G.add_connection("PB1", "PB2", wireSize="1/0", conduitMat="PVC", length=1800.0)
G.add_connection("PB2", "DS3_A", wireSize="1/0", conduitMat="PVC", length=10.0)
G.add_connection("DS3_A", "XFMR2", wireSize="1/0", conduitMat="steel", length=5.0)
G.add_connection("XFMR2", "PNL_B", wireSize=4, conduitMat="steel", length=5.0)
G.add_connection("PNL_B", "DMS_1", wireSize=4, conduitMat="PVC", length=250.0)
G.add_connection("PNL_B", "MCCTV_1", wireSize=4, conduitMat="PVC", length=255.0)


G.add_node("PB3", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("DS1_B", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("XFMR3", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=7.5,
           nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
           nodeType="transformer")
G.add_node("PNL_A_1", phase=1, nodeType="bus", nomVLL=240, nomVLN=120)
G.add_node("CCTV_2", nomVLL=240, phase=1, w=2881.0, vAr=0.0, nodeType="load")
G.add_node("MVDS_2", nomVLN=120, phase=1, w=10.0, vAr=0.0, nodeType="load")
G.add_connection("PB4", "PB3", wireSize="1/0", conduitMat="PVC", length=1430.0)
G.add_connection("PB3", "DS1_B", wireSize="1/0", conduitMat="PVC", length=10.0)
G.add_connection("DS1_B", "XFMR3", wireSize="1/0", conduitMat="steel", length=5.0)
G.add_connection("XFMR3", "PNL_A_1", wireSize=6, conduitMat="steel", length=5.0) #Fix length
G.add_connection("PNL_A_1", "CCTV_2", wireSize=6, conduitMat="PVC", length=50.0) #Fix length
G.add_connection("PNL_A_1", "MVDS_2", wireSize=6, conduitMat="PVC", length=50.0) #Fix length


G.add_node("PB4", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("DS3_B", phase=1, nodeType="bus", nomVLL=480, nomVLN=240)
G.add_node("XFMR4", phase=1, pctR=2.0, pctX=3.0, tapSetting=0.0, rating=7.5,
           nomPrimaryV=480, nomSecondaryV1=120, nomSecondaryV2=240,
           nodeType="transformer")
G.add_node("TADMS_1", nomVLL=240, nomVLN=120, phase=1, w=2000.0, vAr=0.0, nodeType="load")
G.add_connection("PB2", "PB4", wireSize="1/0", conduitMat="PVC", length=1400.0)
G.add_connection("PB4", "DS3_B", wireSize="1/0", conduitMat="PVC", length=10.0)
G.add_connection("DS3_B", "XFMR4", wireSize="1/0", conduitMat="steel", length=5.0)
G.add_connection("XFMR4", "TADMS_1", wireSize=6, conduitMat="PVC", length=15.0)


G1 = RadialPowerSystem("Service #2")
G1.add_node("1", nodeType="service", nomVLL=480, phase=1, availSSC=75000, xRRatio=10.0)
# G1.add_node("2", nomVLL=480, phase=1, w=10000.0, vAr=0.0, nodeType="load")
# G1.add_connection("1", "2", wireSize="6", conduitMat="PVC", length=1400.0, numWires=1)


#########################################################################################
"""Calculations"""
#########################################################################################

plot = True
report = False

# nx.write_gpickle(G, "C:/Users/AtotheM/Desktop/test.gpickle")
# G2 = nx.read_gpickle("C:/Users/AtotheM/Desktop/test.gpickle")
# graphToCheck = G2
graphToCheck = G1
if __name__ == "__main__":
    run_calcs(graphToCheck)
    if report:
        create_report(graphToCheck,
                      outPutPath='C:\Users\AtotheM\Desktop',
                      plotting=plot)
    if plot:
        draw_graph(graphToCheck, outPutPath='C:/Users/AtotheM/Desktop/123.png')
