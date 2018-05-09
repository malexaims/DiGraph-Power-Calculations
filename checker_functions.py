# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 20:50:51 2017

@author: AtotheM
"""
import networkx as nx
from constants import voltageCompatDict


def loop_check(calc_flows_function):
    """Decorator to test for loops. The program is not designed to handle loops between nodes."""
    def loop_check_wrapper(graph, **kwargs):    
        test = True
        try:
           nx.find_cycle(graph, orientation='ignore')
        except Exception:
            test = False
        assert test == False, "Loop detected between nodes. Please correct."
        return calc_flows_function(graph, **kwargs)
    return loop_check_wrapper
    
    
def length_check(calc_flows_function):
    """Decorator to test for edge lengths less than or equal to zero. 
    Such edge lengths are not physically possible."""
    def length_check_wrapper(graph, **kwargs):
        edgeList = graph.edges()
        for begNode, endNode in edgeList:
            edge = graph.get_edge_data(begNode, endNode)
            if edge['length'] <= 0:
                raise ValueError("Conductor lengths must be greater than zero.")
            else:
                pass
        return calc_flows_function(graph, *kwargs)
    return length_check_wrapper


def voltage_check(calc_flows_function):
    """Decorator to test for voltage compatibility of connected nodes."""
    def voltage_check_wrapper(graph, **kwargs):
        incompatList = []
        edgeList = graph.edges()    
        for begNode, endNode in edgeList:
            begType = graph.node[begNode]["nodeType"]
            endType = graph.node[endNode]["nodeType"]
            if begType == "transformer" and endType == "transformer":
                begVoltage = graph.node[begNode]["nomSecondaryV2"] #TODO: Dosent account for nomSecondaryV1, fix.
                endVoltage = graph.node[endNode]["nomPrimaryV"]
            elif begType == "transformer":
                begVoltage = graph.node[begNode]["nomSecondaryV2"] #TODO: Dosent account for nomSecondaryV1, fix.
                endVoltage = graph.node[endNode]["nomVoltage"]
            elif endType == "transformer":
                begVoltage= graph.node[begNode]["nomVoltage"]
                endVoltage = graph.node[endNode]["nomPrimaryV"]
            elif begType != "transformer" and endType != "transformer":
                begVoltage = graph.node[begNode]["nomVoltage"]
                endVoltage = graph.node[endNode]["nomVoltage"]
            try:
                test = endVoltage in voltageCompatDict[str(begVoltage)]
            except KeyError:
                raise ValueError("Nominal Input voltages are not compatible with program for %s." % begNode)
            if not test:
                incompatList.append((begNode, endNode))
        if len(incompatList) > 0:
            raise ValueError("Voltages are not compatible between the following nodes (begNode, endNode):", incompatList)
        return calc_flows_function(graph, **kwargs)
    return voltage_check_wrapper
    
def over_voltage_check(graph, allowableOverVoltage=10.0): #TODO: make allowableOverVoltage a part of the program settings rather than a kwarg?
    """Function to test for loads recieving voltage significantly over thier nomVoltage. Execute after calc_flows()
    and calc_voltages().
    Inputs:
    - graph: power system Digraph
    - allowableOverVoltage: percentage of allowable overVoltage permitted before an exception is raised"""
    incompatList = []
    for i in graph.nodes():
        if graph.node[i]["nodeType"] == "transformer":
            maxVoltage = graph.node[i]["nomPrimaryV"] + graph.node[i]["nomPrimaryV"]*(allowableOverVoltage / 100.0)  
            if graph.node[i]["primaryVoltage"] > maxVoltage:
                incompatList.append(i)
        else: 
            maxVoltage = graph.node[i]["nomVoltage"] + graph.node[i]["nomVoltage"]*(allowableOverVoltage / 100.0)  
            if graph.node[i]["trueVoltage"] > maxVoltage:
                incompatList.append(i)          
    if len(incompatList) > 0:
            raise ValueError("The following nodes are recieving overvoltages in excess of permitted limits:", incompatList)
    return
    
    
    
    