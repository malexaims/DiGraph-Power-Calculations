# -*- coding: utf-8 -*-
"""
Created on Sun May 06 19:22:43 2018

@author: AtotheM
"""

import networkx as nx
import matplotlib.pyplot as plt

#TODO: Implement a better way to scale node labels that are offset from node

def draw_graph(graph, fontSize=8, scaleFactor=0.029, figSize=(1,1), nodeSize=1000, plotDrop=True):
    """Plots a graph visualization with various edge and node labels.
    """

    # scale = len(list(graph.nodes())) * scaleFactor

    pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
    xCoords = sorted([position[0] for node, position in pos.items()])
    yCoords = sorted([position[1] for node, position in pos.items()])

    scale = (((xCoords[-1] - xCoords[0])**2 + (yCoords[-1] - yCoords[0])**2)**0.5) * scaleFactor
    print "scale", scale

    pos1 = {k:[v[0]-scale*1.1,v[1]] for k,v in pos.items()}
    pos1a = {k:[v[0]-scale*1.1,v[1]-scale*0.5] for k,v in pos.items()}
    pos2 = {k:[v[0]+scale*1.4,v[1]] for k,v in pos.items()}

    nx.draw_networkx_nodes(graph, pos,
                           node_color='r',
                           node_size=1000,
                           alpha=1)

    nx.draw_networkx_edges(graph, pos,
                           width=1.0)

    edgeILabels = {(beg,end):'{0:.2f}A'.format(data["I"].real) for beg,end,data in graph.edges(data=True)}

    nodeVLabels = {}
    for i in graph.nodes():
        try:
            if graph.node[i]["nodeType"] == "transformer":
                nodeVLabels[i] = '{0.real:.1f}/{1.real:.1f}V'.format(graph.node[i]["primaryVoltage"], graph.node[i]["secondaryVoltage2"])
            else:
                nodeVLabels[i] = '{0.real:.1f}V'.format(graph.node[i]["trueVoltage"])
        except KeyError:
            pass

    if plotDrop:
        nodeVdLabels = {}
        for i in graph.nodes():
            try:
                pctVdrop = 100.0 * (graph.node[i]["nomVoltage"] - graph.node[i]["trueVoltage"]) / graph.node[i]["nomVoltage"]
                nodeVdLabels[i] = '{0.real:.1f} % Drop'.format(pctVdrop)
            except KeyError:
                pass

    nodeSSCLabels = {}
    for i in graph.nodes():
        try:
            nodeSSCLabels[i] = '{0.real:.1f} SSC_LL'.format(graph.node[i]["SymSSC"])
        except KeyError:
            pass


    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edgeILabels, font_size=fontSize)
    nx.draw_networkx_labels(graph, pos1, nodeVLabels, font_size=fontSize)
    nx.draw_networkx_labels(graph, pos1a, nodeVdLabels, font_size=fontSize)
    nx.draw_networkx_labels(graph, pos2, nodeSSCLabels, font_size=fontSize)
    nx.draw_networkx_labels(graph, pos, font_size=fontSize)

    plt.axis('off')
    plt.rcParams["figure.figsize"] = [i for i in figSize]
    plt.show()
