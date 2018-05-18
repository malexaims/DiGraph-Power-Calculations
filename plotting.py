# -*- coding: utf-8 -*-
"""
Created on Sun May 06 19:22:43 2018

@author: AtotheM
"""

import networkx as nx
import matplotlib.pyplot as plt

def draw_graph_labels(graph):
    """Plots a graph visualization with various edge and node labels.
    """
    pos = nx.spring_layout(graph)
    pos1 = {k:[v[0],v[1]-0.15] for k,v in pos.items()}
    pos2 = {k:[v[0],v[1]-0.30] for k,v in pos.items()}

    nx.draw_networkx_nodes(graph, pos,
                           node_color='r',
                           node_size=1000,
                           alpha=1)

    nx.draw_networkx_edges(graph, pos,
                           width=1.0,
                           arrowsize=25)

    edgeILabels = {(beg,end):'I: {0:.2f} A'.format(data["I"]) for beg,end,data in graph.edges(data=True)}

    nodeVLabels = {}
    for i in graph.nodes():
        try:
            if graph.node[i]["nodeType"] == "transformer":
                nodeVLabels[i] = '{0.real:.1f}/{1.real:.1f} V'.format(graph.node[i]["primaryVoltage"], graph.node[i]["secondaryVoltage2"])
            else:
                nodeVLabels[i] = '{0.real:.1f} V'.format(graph.node[i]["trueVoltage"])
        except KeyError:
            print "!"
            pass

    nodeSSCLabels = {}
    for i in graph.nodes():
        try:
            nodeSSCLabels[i] = '{0.real:.1f} I_Sym_SSC'.format(graph.node[i]["SymSSC"])
        except KeyError:
            print "!"
            pass

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edgeILabels, font_size=12)
    nx.draw_networkx_labels(graph, pos1, nodeVLabels, font_size=12)
    nx.draw_networkx_labels(graph, pos2, nodeSSCLabels, font_size=12)
    nx.draw_networkx_labels(graph, pos, font_size=12)

    plt.axis('off')
    plt.rcParams["figure.figsize"] = [10,10]
    plt.show()


def draw_graph_gv(graph):
    """Plots a graph visualization with various edge and node labels.
    """
    # gVis = nx.nx_agraph.to_agraph(graph)
    pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
    pos1 = {k:[v[0]-15,v[1]] for k,v in pos.items()}
    pos2 = {k:[v[0]+25,v[1]] for k,v in pos.items()}

    nx.draw_networkx_nodes(graph, pos,
                           node_color='r',
                           node_size=1000,
                           alpha=1)

    nx.draw_networkx_edges(graph, pos,
                           width=1.0,
                           arrowsize=25)

    edgeILabels = {(beg,end):'{0:.2f} A'.format(data["I"].real) for beg,end,data in graph.edges(data=True)}

    nodeVLabels = {}
    for i in graph.nodes():
        try:
            if graph.node[i]["nodeType"] == "transformer":
                nodeVLabels[i] = '{0.real:.1f}/{1.real:.1f} V'.format(graph.node[i]["primaryVoltage"], graph.node[i]["secondaryVoltage2"])
            else:
                nodeVLabels[i] = '{0.real:.1f} V'.format(graph.node[i]["trueVoltage"])
        except KeyError:
            pass

    nodeSSCLabels = {}
    for i in graph.nodes():
        try:
            nodeSSCLabels[i] = '{0.real:.1f} Sym_SSC_LL'.format(graph.node[i]["SymSSC"])
        except KeyError:
            pass

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edgeILabels, font_size=8)
    nx.draw_networkx_labels(graph, pos1, nodeVLabels, font_size=8)
    nx.draw_networkx_labels(graph, pos2, nodeSSCLabels, font_size=8)
    nx.draw_networkx_labels(graph, pos, font_size=8)

    plt.axis('off')
    plt.rcParams["figure.figsize"] = [10,10]
    plt.show()
