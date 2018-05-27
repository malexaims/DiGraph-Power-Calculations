# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 21:01:56 2017

@author: AtotheM
"""
import math
import networkx as nx

def get_node_voltage(graph, i):
    """Helper function to return node voltage when VLL and VLN need to be considered.
    Only works for node and bus type loads.
    """
    voltage = 0
    try:
        voltage = graph.node[i]["nomVLL"]
    except KeyError:
        try:
            voltage = graph.node[i]["nomVLN"]
        except KeyError:
            raise Exception("Incorrect VLL or VLN voltage setting for node {}".format(i))
    return voltage


# def get_pf_theta(w, vAr):
#     """Helper function that returns power factor and theta values given vA and vAr."""
#     W = math.sqrt(w**2 - vAr**2)
#     powerFactor = W / vA
#     theta = math.acos(powerFactor)
#     return powerFactor, theta
#
#
# def get_pctZ(pctR, pctX):
#     """Helper function that returns pctZ given pctR and pctX."""
#     return math.sqrt(pctR**2 + pctX**2)
#
