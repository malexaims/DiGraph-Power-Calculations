# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 07:53:19 2017

@author: AtotheM
"""

import networkx as nx
import math
from checker_functions import loop_check, length_check, voltage_check
from constants import WBASE, VARBASE


#TODO: Currently transformers need to have nomSecondaryV2 and nomSecondaryV1. Fix to only require V1 for transformers
#with single voltage outputs. Can this be accomplished when inputting transformer data?

#TODO: Write a function that checks the capacity of transformers. Needs to account for single phase loads being
#connected to three phase transformers (1/3 capacity)."""

#TODO: Write a function that sizes wire sizes based on permitted ampacity.

#TODO: Write a function that sizes wires based on voltage drop permitted to furthest load. Wire size required for ampacity
#needs to be the lower bound.

#TODO: Need to account for three phase faults and single phase L-G faults to expand SSC calculations.

#TODO: Add conversion of fault current from PU to actual.

#TODO: Figure out if voltage drop accross transformer is working when a single phase load is connected to a three phase transformer secondaryVoltage

#TODO: Need to check if three-phase and single phase load mixtures are being properly addressed


def per_unit_conv(graph):
    """Converts a eletrical network to the per unit system.
    """
    #Define base power with random assumption
    wBase, vArBase = WBASE, VARBASE
    sBase = complex(wBase, vArBase)
    #Set the voltage bases for each edge. Node bases will come from nominal voltage settings.
    for beg,end,data in graph.edges(data=True):
        if graph.in_degree(beg) == 0:
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
            data["zBase"] = complex(((data["vBase"].real**2.0) / sBase.real), ((data["vBase"].imag**2.0) / sBase.imag))
        except KeyError:
            print "Voltage Base not set for edge:", i
    #Calculate the per unit impedance of all nodes and egdes.
    #TODO: Determine better way to treat source impedance since generators will have non negligable internal impedance. Service nodes dont have a impedance attribute currently.
    for i in graph.nodes():
        #For loads
        if graph.node[i]["nodeType"] == "load":
            zPU = ((graph.node[i]["nomVoltage"]**2.0) / complex(graph.node[i]["w"], graph.node[i]["vAr"])) / graph.node[i]["zBase"]
            graph.node[i]["zPU"] = zPU
        #For transformers
        if graph.node[i]["nodeType"] == "transformer":

            zPU = (complex(graph.node[i]["pctR"]/100.0,graph.node[i]["pctX"]/100.0) * (sBase / (graph.node[i]["rating"]*1000.0)) *
                  ((graph.node[i]["nomPrimaryV"] - (graph.node[i]["nomPrimaryV"] * graph.node[i]["tapSetting"])) /
                  graph.node[i]["nomPrimaryV"])**2.0)

            graph.node[i]["zPU"] = complex(-zPU.real,zPU.imag)
    #For edges
    for beg,end,data in graph.edges(data=True):
        data["zPU"] = complex(((data["rL"] * data["length"])/1000.0), ((data["xL"] * data["length"])/1000.0)) / data["zBase"]
    #Calculate the per unit current requirements of each load and transformer (power consumption)
    for i in graph.nodes():
        try:
            if graph.node[i]["nodeType"] == "load":
               graph.node[i]["wPU"] = graph.node[i]["w"] / WBASE
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
    as the 'w' and 'vArPU' attribuite. Also calculates the total load required at the service point, then assigns these
    values to the service node as negative float for outgoing power flow.
    """
    #Sum total per unit current of the system
    wPUTotal = 0
    vArPUTotal = 0
    for i in graph.nodes():
        if graph.node[i]["nodeType"] == "service":
            pass
        try:
            wPUTotal += graph.node[i]["wPU"]
            vArPUTotal += graph.node[i]["vArPU"]
        except KeyError:
            pass
    for i in graph.nodes():
    #Find the service node and set the total per unit current
        try:
            if graph.node[i]["nodeType"] == "service":
                graph.node[i]["wPU"] = -wPUTotal
                graph.node[i]["vArPU"] = -vArPUTotal
                graph.node[i]["trueVoltagePU"] = 1.0 #Service PU voltage will always be 1
        except KeyError:
            pass
    #Create dict of real flow between network nodes
    wFlowsDict = nx.network_simplex(graph, demand="wPU")[1]
    #Assign per unit to each edge in the graph
    for k,v in wFlowsDict.items():
        if len(wFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in wFlowsDict[k].items():
            graph[k][k1]["wPU"] = v1
    #Create dict of imag flow between network nodes
    vArFlowsDict = nx.network_simplex(graph, demand="vArPU")[1]
    #Assign per unit to each edge in the graph
    for k,v in vArFlowsDict.items():
        if len(vArFlowsDict[k].values()) == 0:
            pass
        for k1,v1 in vArFlowsDict[k].items():
            graph[k][k1]["vArPU"] = v1
    if debug:
        print wPUTotal
        print vArPUTotal
        print wFlowsDict
        print vArFlowsDict


def actual_conv(graph):
    """Converts a eletrical network from the per unit system to actual values.
    """
    #Calculate actual vDrop and current on each edge
    for beg,end,data in graph.edges(data=True):
        data["vDrop"] = data["vDropPU"] * data["vBase"]
        if graph.node[end]["phase"] == 3:
            data["I"] = data["IPU"] * (data["vBase"]/(data["zBase"] * math.sqrt(3)))
        else:
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
    trueVoltagePU minus the per unit voltage drop along the interconnecting edge.
    """
    edge = graph.get_edge_data(sourceNode, endNode)
    wPU = edge["wPU"]
    vArPU = edge["vArPU"]
    zPU = edge["zPU"]
    phaseEnd = graph.node[endNode]["phase"]
    if graph.node[sourceNode]["nodeType"] == "transformer" and graph.node[endNode]["nodeType"] == "transformer":
        vSPU = graph.node[sourceNode]["nomSecondaryV2"] / graph.node[endNode]["nomPrimaryV"]#TODO: Fix for transformers with one voltage secondary
    elif graph.node[sourceNode]["nodeType"] == "transformer":
        vSPU = graph.node[sourceNode]["nomSecondaryV2"] / graph.node[endNode]["nomVoltage"] #TODO: Fix for transformers with one voltage secondary
    elif graph.node[endNode]["nodeType"] == "transformer":
        vSPU = graph.node[sourceNode]["nomVoltage"] / graph.node[endNode]["nomPrimaryV"]
    else:
        vSPU = 1
    IPU = complex(wPU, vArPU) / vSPU
    #Set current flowing along each edge
    edge["IPU"] = IPU
    #Calculate round-trip voltage drop along edge
    if phaseEnd == 1:
        #Reactance must be negative for voltage drop to work correctly
        vDropPU = complex(IPU.real,-IPU.imag) * zPU * 2.0
    elif phaseEnd == 3:
        vDropPU = math.sqrt(3) * complex(IPU.real,-IPU.imag) * zPU
    else:
        raise ValueError("Phase value for edge must be 1 or 3")
    assert vDropPU.real < 1.0, ("Segment voltge drop exceeds starting voltage between {0} and {1}."
                                 " Check network configuration and inputs.".format(sourceNode, endNode))
    #Check for nodes that are transformers and treat them specially
    edge["vDropPU"] = vDropPU
    if graph.node[endNode]["nodeType"] == "transformer":
        if graph.node[sourceNode]["nodeType"] == "transformer":
            graph.node[endNode]["primaryVoltagePU"] = graph.node[sourceNode]["secondaryVoltagePU"] - vDropPU
        else:
            graph.node[endNode]["primaryVoltagePU"] = graph.node[sourceNode]["trueVoltagePU"] - vDropPU
        #Set transformer secondary voltage
        successors = [i for i in graph.successors(endNode)]
        if len(successors) > 1:
            raise ValueError("""Transformer secondaries may only be directly connected to one
            successor node.""")

        graph.node[endNode]["secondaryVoltagePU"] = ((graph.node[endNode]["primaryVoltagePU"] -
                                                    (graph.node[endNode]["primaryVoltagePU"] * graph.node[endNode]["tapSetting"])) -
                                                    (IPU * ((graph.node[endNode]["nomSecondaryV2"]/graph.node[endNode]["nomPrimaryV"])**2.0 /
                                                    graph.node[endNode]["zPU"]))) #TODO: Fix for transformers with two voltage secondaries... does this even need to be handled?
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
    each edge, set edge per unit currents, and to assign the trueVoltagePU to each node.
    """
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


def calc_sym_ssc(graph):
    """Calculates the maximum symmetrical short circuit current at each node on the network, starting from the "service" node
    then running down the digraph edges out to the load nodes. The series impedance from the "service" node
    to each other node on the network is used to calculate the short circuit current available. Determines and sets
    three-phase faults for three-phase nodes, and single line to ground faults and line to line faults for single phase nodes. Only
    function for symmetrical faults in three phase and single phase systems. Requires that the short circuit current avaliable is provided
    for the secondary terminals of the service transformer.
    """
    wBase, vArBase = WBASE, VARBASE
    sBase = complex(wBase, vArBase)
    serviceNode = None

    for i in graph.nodes():
        if graph.in_degree(i) == 0:
            serviceNode = i
            break

    try:
        zBase = (graph.node[serviceNode]["nomVoltage"]**2.0) / sBase
        sourceZPU = (graph.node[serviceNode]["nomVoltage"] / graph.node[serviceNode]["sscXfmrSec"]) / zBase
    except KeyError:
        print ("""Missing input data for service node. Unable to perform short circuit current calculations.
                  Avaliable short circuit current on secondary of service transformer.""")

    for i in graph.nodes():
        #Move on from service node
        if graph.in_degree(i) == 0:
            continue
        length, path = nx.bidirectional_dijkstra(graph, serviceNode, i)
        #TODO: Implement way to start with a starting SSC that sets a upstream system impedance
        zSeriesPU = sourceZPU #Start with service impedance from source
        #Sum series edge impedances between service point and node
        for j in range(len(path)-1):
            try:
                zSeriesPU += graph[path[j]][path[j+1]]["zPU"]
            except KeyError:
                print "zPU not set for edge between {0} and {1}".format(path[j], path[j+1])
        #If transformer is on the path add that to the series Impedance
        for y in path:
            if graph.node[y]["nodeType"] == "transformer":
                try:
                    zSeriesPU += graph.node[y]["zPU"]
                except KeyError:
                    print "zPU not set for transformer {0}".format(y)
        #If transformer is the node where zSeriesPU is being set, dont include that transformers impedance (ssc at primary)
        if graph.node[i]["nodeType"] == "transformer":
                graph.node[i]["zSeriesPU"] = zSeriesPU - graph.node[i]["zPU"]
                continue
        graph.node[i]["zSeriesPU"] = zSeriesPU

    for i in graph.nodes():
        if graph.in_degree(i) == 0:
            serviceNode = i
            continue
        if graph.node[i]["phase"] == 1:
            try:
                if graph.node[i]["nodeType"] == "transformer":
                    graph.node[i]["SymSSC"] =  (1.0 / graph.node[i]["zSeriesPU"]) * (sBase / graph.node[i]["nomPrimaryV"])
                else:
                    graph.node[i]["SymSSC"] =  (1.0 / graph.node[i]["zSeriesPU"]) * (sBase / graph.node[i]["nomVoltage"])
            except KeyError:
                print "Missing series per unit impedance for node {0}".format(i)

        #TODO: Implement SSC for three phase systems
        # if graph.node[i]["phase"] == 3:
        #     try:
        #         if graph.node[i]["nodeType"] == "transformer":
        #             graph.node[i]["SymSSC"] = (3*graph.node[i]["nomPrimaryV"]**2/math.sqrt(3) / -graph.node[i]["zSeriesPU"]) / sBase #TODO: Fix voltage determination for LN
        #         else:
        #             graph.node[i]["SymSSC"] = (3*graph.node[i]["nomVoltage"]**2/math.sqrt(3) / -graph.node[i]["zSeriesPU"]) / sBase #TODO: Fix voltage determination for LN
        #     except KeyError:
        #         print "Missing series per unit impedance for node {0}".format(i)
