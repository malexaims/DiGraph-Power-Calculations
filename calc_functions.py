# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 07:53:19 2017

@author: AtotheM
"""

import networkx as nx
import math
from checker_functions import loop_check, length_check, voltage_check
from helper_functions import get_pf_theta
from constants import VABASE, VARBASE


#TODO: Currently transformers need to have nomSecondaryV2 and nomSecondaryV1. Fix to only require V1 for transformers
#with single voltage outputs. Can this be accomplished when inputting transformer data?

#TODO: Write a function that checks the capacity of transformers. Needs to account for single phase loads being
#connected to three phase transformers (1/3 capacity)."""

#TODO: Write a function that sizes wire sizes based on permitted ampacity.

#TODO: Write a function that sizes wires based on voltage drop permitted to furthest load. Wire size required for ampacity
#needs to be the lower bound.

#TODO: Write a function that calculates falt currents and places this information on each node. Need to account 
#for three phase faults and single phase L-L and L-G faults at a minimum.

#TODO: Make function to create wires as edges with data input from the conductor dataframe ot calculate R and X values
#from input material and AWG sizes.

    
@loop_check  
@length_check
@voltage_check
def calc_flows(graph, debug=False):
    """Calculates the load flow on each edge for the entire graph, then assigns the value to the edges
    as the 'vAFlow' and 'vARFlow' attributes for volt-amps and volt-amps-reactive respectively. 
    Also calculates the total load required at the service point, then assigns this value to the 
    service node as the attribute 'totalLoad': a negative float.
    """
    totalVa = 0
    totalVar = 0
    #Sum real and reactive power flows
    for i in graph.nodes():
        try:
            totalVa += graph.node[i]["vA"]
            totalVar += graph.node[i]["vAr"]
        except KeyError:
            pass 
    for i in graph.nodes():
    #Find the service node and set the service node trueVoltage
        try:      
            if graph.node[i]["nodeType"] == "service":
                graph.node[i]["vA"] = -totalVa
                graph.node[i]["vAr"] = -totalVar
                graph.node[i]["trueVoltage"] = graph.node[i]["nomVoltage"]
        except KeyError:
            pass
    #Create dict of real power flow between network nodes
    vAFlowsDict = nx.network_simplex(graph, demand="vA")[1]
    #Assign flows to each edge in the graph
    for k,v in vAFlowsDict.items():
        if len(vAFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in vAFlowsDict[k].items():
            graph[k][k1]["vAFlow"] = v1
    #Create dict of reactive power flow between network nodes
    vArFlowsDict = nx.network_simplex(graph, demand="vAr")[1]
    #Assign flows to each edge in the graph
    for k,v in vArFlowsDict.items():
        if len(vArFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in vArFlowsDict[k].items():
            graph[k][k1]["vARFlow"] = v1
    if debug:
        print totalVa
        print totalVar
        print vAFlowsDict
        print vArFlowsDict


def segment_vdrop_current(graph, sourceNode, endNode):
    """Calculates the voltage drop along an edge, and sets the trueVoltage of the 
    endNode along with the current along the edge. The trueVoltage is the sourceNode 
    trueVoltage minus the voltage drop along the interconnecting edge."""
    edge = graph.get_edge_data(sourceNode, endNode)
    vA = edge["vAFlow"]
    vAr = edge["vARFlow"]
    xL = edge["xL"]
    rL = edge["rL"]
    length = edge["length"]
    phaseEnd = graph.node[sourceNode]["phase"]
    if graph.node[sourceNode]["nodeType"] == "transformer":
        vS = graph.node[sourceNode]["secondaryVoltage"] #TODO: Fix this... it is wrong need to use the base voltage for current calcs
    else:
        vS = graph.node[sourceNode]["trueVoltage"] #TODO: Fix this... it is wrong need to use the base voltage for current calcs
    I = vA / vS
   #Set current flowing along each edge
    edge["I"] = I
   #Calculate conductor total resistance and reactance
    xT = xL * length / 1000.0
    rT = rL * length / 1000.0
    #Determine powerFactor and theta
    powerFactor, theta = get_pf_theta(vA,vAr)
    #Calculate round-trip voltage drop along edge
    if phaseEnd == 1:
        vDrop = (2.0*(vS + I*rT*math.cos(theta) + I*xT*math.sin(theta) - 
        math.sqrt(vS**2 - (I*xT*math.cos(theta) - I*rT*math.cos(theta))**2)))
    elif phaseEnd == 3:
        vDrop = (math.sqrt(3)*(vS + I*rT*math.cos(theta) + I*xT*math.sin(theta) - 
        math.sqrt(vS**2 - (I*xT*math.cos(theta) - I*rT*math.cos(theta))**2)))
    else:
        raise ValueError("Phase value for edge must be 1 or 3")
    assert vDrop < vS, "Segment voltge drop exceeds starting voltage. Check network configuration."
    #Check for nodes that are transformers and treat them specially
    if graph.node[endNode]["nodeType"] == "transformer":
        if graph.node[sourceNode]["nodeType"] == "transformer":
            graph.node[endNode]["primaryVoltage"] = graph.node[sourceNode]["secondaryVoltage"] - vDrop
            return
        graph.node[endNode]["primaryVoltage"] = graph.node[sourceNode]["trueVoltage"] - vDrop
        #Set transformer secondary voltage 
        successors = [i for i in graph.successors(endNode)]
        if len(successors) > 1:
            raise ValueError("""Transformer secondaries may only be directly connected to one 
            successor node.""")
        transformer_voltage(graph, endNode, successors[0])
        return
    if graph.node[sourceNode]["nodeType"] == "transformer":
        graph.node[endNode]["trueVoltage"] = graph.node[sourceNode]["secondaryVoltage"] - vDrop
        return
    else:
        graph.node[endNode]["trueVoltage"] = graph.node[sourceNode]["trueVoltage"] - vDrop
        return
  
  
def calc_voltages(graph):
    """Calculates the trueVoltage for each node on the network, starting from the "service" node 
    then running down the digraph edges out to the load nodes using an oriented depth-first created 
    tree of the graph structure. The segment_vdrop_current function is used to calculate the voltage drop along 
    each edge, set edge currents, and to assign the trueVoltage to each node."""
    #Find the serviceNode
    serviceNode = None
    for i in graph.nodes():
        if graph.in_degree(i) == 0:
            serviceNode = i
            break
    #Oriented tree structure of digraph starting at serviceNode
    graphStructure = nx.edge_dfs(graph, source=serviceNode)
    #Calculate voltages starting at source and working towards loads
    for i in graphStructure:
        segment_vdrop_current(graph, i[0], i[1])
 
      
def transformer_voltage(graph, transformerNode, loadNode):
    """Calculates the actual secondaryVoltage based on applied primaryVoltage, turnsRatio, 
    and vDrop across transformer.
    Inputs:
    - graph: power system Digraph
    - loadNode: load connected to transformer secondary
    - transformerNode: transformer to calculate secondaryVoltage for
    
    Obtained from input nodes:
    - primaryVoltage: applied voltage at transformer primary terminals
    - rating: nameplate rating of transformer in kVA
    - transformerPhase: transformer phase configuration (one or three)
    - loadPhase: load node phase configuration (one or three)
    - vA: real power flow out of secondary
    - vAr: reactive power flow out of secondary
    - nomPrimaryV: transformer nameplate primary voltage
    - nomSecondaryV1: transformer nameplate phase to ground voltage
    - nomSecondaryV2: transformer nameplate phase to phase voltage
    - nomLoadV: nominal voltage of load node
    - tapSetting: transformer tap setting -- positive indicates FCBN taps, 
    and negative indicates FCAN taps
    - pctR: transformer per unit resistance in percentage
    - pctX: transformer per unit reactance in percentage
    """
    primaryVoltage = graph.node[transformerNode]["primaryVoltage"]
    rating = graph.node[transformerNode]["rating"]
    nomPrimaryV = graph.node[transformerNode]["nomPrimaryV"]
    nomSecondaryV1 = graph.node[transformerNode]["nomSecondaryV1"] #TODO: Fix to account for transformers with single voltage output
    nomSecondaryV2 = graph.node[transformerNode]["nomSecondaryV2"] #TODO: Fix to account for transformers with single voltage output only
    nomLoadV = graph.node[loadNode]["nomVoltage"]
    tapSetting = graph.node[transformerNode]["tapSetting"]
    pctR = graph.node[transformerNode]["pctR"]
    pctX = graph.node[transformerNode]["pctX"]
    loadPhase = graph.node[loadNode]["phase"]
    #Edge from secondary to connected node
    outEdge = graph.get_edge_data(transformerNode, loadNode)
    vA = outEdge["vAFlow"]
    vAr = outEdge["vARFlow"]
    #Calculate turns ratio, accounting for tap settings
    if int(nomSecondaryV1) / int(nomLoadV) == 1:
        turnsRatio = (nomPrimaryV - (nomPrimaryV*tapSetting)) / nomSecondaryV1
    elif int(nomSecondaryV2) / int(nomLoadV) == 1:
        turnsRatio = (nomPrimaryV - (nomPrimaryV*tapSetting)) / nomSecondaryV2
    else:
        raise ValueError("Load voltage and transformer secondary voltage are not compatible.")
    #Determine actual X (xA) and actual R (rA) in ohms
    actual = lambda pct: (10.0*(pct)*(nomLoadV / 1000.0)**2) / (rating)
    rA = actual(pctR)
    xA = actual(pctX)
    I = vA / nomLoadV
    pf, theta = get_pf_theta(vA, vAr)
    if loadPhase == 1:
        vDrop = I*(rA*math.cos(theta) + xA*math.sin(theta))
    elif loadPhase == 3:
        vDrop = math.sqrt(3)*I*(rA*math.cos(theta) + xA*math.sin(theta))
    else:
        raise ValueError("Load phase configuration connected to transformer is incorrect.")
    graph.node[transformerNode]["secondaryVoltage"] = (primaryVoltage / turnsRatio) - vDrop   

    
def per_unit_conv(graph):
    """Converts a eletrical network to the per unit system."""
    #Define base power with random assumption
    vABase, vArBase = VABASE, VARBASE
    sBase = complex(vABase, vArBase)
    #Set the voltage bases for each edge. Node bases will come from nominal voltage settings.
    for beg,end,data in graph.edges(data=True):
        if graph.node[beg]["nodeType"] == "service":
            data["vBase"] = graph.node[beg]["nomVoltage"]
        if graph.node[end]["nodeType"] == "transformer":
            data["vBase"] = graph.node[end]["nomPrimaryV"]
        else:
            try:
                data["vBase"] = graph.node[end]["nomVoltage"]
            except KeyError:
                pass
    #Set the Zbases for all nodes except transformers (dont need to for transformers)
    for i in graph.nodes():
        if graph.node[i]["nodeType"] == "load":
            try:
                graph.node[i]["zBase"] = (graph.node[i]["nomVoltage"]**2.0) / sBase
            except KeyError:
                print "Voltage Base not set for node:", i
    #Set the ZBases for all edges
    for beg,end,data in graph.edges(data=True):
        try:
            data["zBase"] = (data["vBase"]**2.0) / sBase
        except KeyError:
            print "Voltage Base not set for edge:", i
    #Calculate the per unit impedance of all nodes and egdes. Service has no internal impedance.
    #TODO: Determine better way to treat source impedance since generators will have non negligable internal impedance. Service nodes dont have a impedance attribute currently.
    for i in graph.nodes():
        #For loads
        if graph.node[i]["nodeType"] == "load":
            zPU = ((graph.node[i]["nomVoltage"]**2.0) / complex(graph.node[i]["vA"], graph.node[i]["vAr"])) / graph.node[i]["zBase"]
            graph.node[i]["zPU"] = zPU
        #For transformers
        if graph.node[i]["nodeType"] == "transformer":
            
            zPU = complex(graph.node[i]["pctR"],graph.node[i]["pctX"]) * (sBase / (graph.node[i]["rating"]*1000.0)) * \
                  ((graph.node[i]["nomPrimaryV"] - (graph.node[i]["nomPrimaryV"] * graph.node[i]["tapSetting"])) / \
                  graph.node[i]["nomPrimaryV"])**2.0
            
            graph.node[i]["zPU"] = zPU
    #For edges
    for beg,end,data in graph.edges(data=True):
        data["zPU"] = complex(((data["rL"] * data["length"])/1000.0), ((data["xL"] * data["length"])/1000.0)) / data["zBase"]
    #Calculate the per unit current requirements of each load and transformer (power consumption)
    for i in graph.nodes():
        try:
            if graph.node[i]["nodeType"] == "load":
               graph.node[i]["vAPU"] = graph.node[i]["vA"] / VABASE
               graph.node[i]["vArPU"] = graph.node[i]["vAr"] / VARBASE
            else:
                pass
        except KeyError:
            pass
        
@loop_check  
@length_check
@voltage_check
def calc_flows_PU(graph, debug=False):
    """Calculates the per unit load flow on each edge for the entire graph, then assigns the value to the edges
    as the 'vAPU' and 'vArPU' attribuite. Also calculates the total load required at the service point, then assigns these 
    values to the service node as negative float for outgoing power flow.
    """
    #Sum total per unit current of the system  
    vAPUTotal = 0
    vArPUTotal = 0
    for i in graph.nodes():
        if graph.node[i]["nodeType"] == "service":
            pass
        try:
            vAPUTotal += graph.node[i]["vAPU"]
            vArPUTotal += graph.node[i]["vArPU"]
        except KeyError:
            pass 
    for i in graph.nodes():
    #Find the service node and set the total per unit current
        try:      
            if graph.node[i]["nodeType"] == "service":
                graph.node[i]["vAPU"] = -vAPUTotal
                graph.node[i]["vArPU"] = -vArPUTotal
                graph.node[i]["trueVoltagePU"] = 1.0 #Service PU voltage will always be 1
        except KeyError:
            pass
    #Create dict of real flow between network nodes
    vAFlowsDict = nx.network_simplex(graph, demand="vAPU")[1]
    #Assign per unit to each edge in the graph
    for k,v in vAFlowsDict.items():
        if len(vAFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in vAFlowsDict[k].items():
            graph[k][k1]["vAPU"] = v1
    #Create dict of imag flow between network nodes
    vArFlowsDict = nx.network_simplex(graph, demand="vArPU")[1]
    #Assign per unit to each edge in the graph
    for k,v in vArFlowsDict.items():
        if len(vArFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in vArFlowsDict[k].items():
            graph[k][k1]["vArPU"] = v1
    if debug:
        print vAPUTotal
        print vArPUTotal
        print vAFlowsDict
        print vArFlowsDict
                   
                   
def actual_conv(graph):
    """Converts a eletrical network from the per unit system to actual values."""
    #Calculate actual vDrop and current on each edge
    for beg,end,data in graph.edges(data=True):
        data["vDrop"] = data["vDropPU"] * data["vBase"]
        data["I"] = data["IPU"] * (data["vBase"]/data["zBase"])
    #Calculate actual voltage at each edge
    for i in graph.nodes():
        if graph.node[i]["nodeType"] == "service":
            pass
        if graph.node[i]["nodeType"] == "transformer":
            graph.node[i]["primaryVoltage"] = graph.node[i]["primaryVoltagePU"] * graph.node[i]["nomPrimaryV"]
            graph.node[i]["secondaryVoltage1"] = graph.node[i]["secondaryVoltagePU"] * graph.node[i]["nomSecondaryV1"] #TODO: Transformers with only one secondary voltage
            graph.node[i]["secondaryVoltage2"] = graph.node[i]["secondaryVoltagePU"] * graph.node[i]["nomSecondaryV2"] #TODO: Transformers with only one secondary voltage
        else:
            graph.node[i]["trueVoltage"] = graph.node[i]["trueVoltagePU"] * graph.node[i]["nomVoltage"]

def segment_vdrop_PU(graph, sourceNode, endNode):
    """Calculates the per unit voltage drop along an edge, and sets the trueVoltagePU of the 
    endNode along with the per unit current along the edge. The trueVoltagePU is the sourceNode 
    trueVoltagePU minus the per unit voltage drop along the interconnecting edge."""    
    edge = graph.get_edge_data(sourceNode, endNode)
    vAPU = edge["vAPU"]
    vArPU = edge["vArPU"]
    zPU = edge["zPU"]
    phaseEnd = graph.node[sourceNode]["phase"]
    if graph.node[sourceNode]["nodeType"] == "transformer":
        vSPU = graph.node[sourceNode]["nomSecondaryV2"] / graph.node[endNode]["nomVoltage"] #TODO: Fix for transformers with one voltage secondary  
    if graph.node[endNode]["nodeType"] == "transformer":
        vSPU = graph.node[sourceNode]["nomVoltage"] / graph.node[endNode]["nomPrimaryV"]
    else:
        vSPU = 1 
    IPU = complex(vAPU, vArPU) / vSPU
    #Set current flowing along each edge
    edge["IPU"] = IPU
    #Calculate round-trip voltage drop along edge
    if phaseEnd == 1:
        vDropPU = IPU * zPU * 2.0
    elif phaseEnd == 3:
        vDropPU = math.sqrt(3) * IPU * zPU
    else:
        raise ValueError("Phase value for edge must be 1 or 3")
    assert vDropPU.real < 1.0, "Segment voltge drop exceeds starting voltage. Check network configuration."
    #Check for nodes that are transformers and treat them specially
    edge["vDropPU"] = vDropPU
    if graph.node[endNode]["nodeType"] == "transformer":
        if graph.node[sourceNode]["nodeType"] == "transformer":
            graph.node[endNode]["primaryVoltagePU"] = graph.node[sourceNode]["secondaryVoltagePU"] - vDropPU
            return
        graph.node[endNode]["primaryVoltagePU"] = graph.node[sourceNode]["trueVoltagePU"] - vDropPU
        #Set transformer secondary voltage 
        successors = [i for i in graph.successors(endNode)]
        if len(successors) > 1:
            raise ValueError("""Transformer secondaries may only be directly connected to one 
            successor node.""")
#        graph.node[endNode]["secondaryVoltagePU"] = (graph.node[endNode]["primaryVoltagePU"] - 
#                                                    (IPU * ((graph.node[endNode]["nomSecondaryV2"]/graph.node[endNode]["nomPrimaryV"])**2.0 / 
#                                                    graph.node[endNode]["zPU"])))
                                                    
        graph.node[endNode]["secondaryVoltagePU"] = ((graph.node[endNode]["primaryVoltagePU"] - 
                                                    (graph.node[endNode]["primaryVoltagePU"] * graph.node[endNode]["tapSetting"])) - 
                                                    (IPU * ((graph.node[endNode]["nomSecondaryV2"]/graph.node[endNode]["nomPrimaryV"])**2.0 / 
                                                    graph.node[endNode]["zPU"])))
        return
    if graph.node[sourceNode]["nodeType"] == "transformer":
        graph.node[endNode]["trueVoltagePU"] = graph.node[sourceNode]["secondaryVoltagePU"] - vDropPU
        return
    else:
        graph.node[endNode]["trueVoltagePU"] = graph.node[sourceNode]["trueVoltagePU"] - vDropPU
        return
    
def calc_voltages_PU(graph):
    """Calculates the trueVoltagePU for each node on the network, starting from the "service" node 
    then running down the digraph edges out to the load nodes using an oriented depth-first created 
    tree of the graph structure. The segment_vdrop_PU function is used to calculate the per unit voltage drop along 
    each edge, set edge per unit currents, and to assign the trueVoltagePU to each node."""
    #Find the serviceNode
    serviceNode = None
    for i in graph.nodes():
        if graph.in_degree(i) == 0:
            serviceNode = i
            break
    #Oriented tree structure of digraph starting at serviceNode
    graphStructure = nx.edge_dfs(graph, source=serviceNode)
    #Calculate voltages starting at source and working towards loads
    for i in graphStructure:
        segment_vdrop_PU(graph, i[0], i[1])

    
    
    
    
    
    
    
    
    
    
    
    
    