# -*- coding: utf-8 -*-
"""
Created on Sun May 06 19:22:43 2018

@author: AtotheM
"""
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image


def draw_graph(graph, outPutPath=None, fontSize=10):
    """Plots a graph visualization with various edge and node labels.
    """
    try:
        fontSize = str(fontSize)
    except TypeError:
        print "Incorrect fontSize kwarg input"
    if outPutPath == None:
        raise Exception("Output path required for draw_graph()")
    # scale = len(list(graph.nodes())) * scaleFactor

    aGraph = nx.nx_agraph.to_agraph(graph)

    for edge in aGraph.edges_iter():
        edge.attr['label'] = '{0:.2f}A'.format(graph[edge[0]][edge[1]]["I"].real)

    for n in aGraph.nodes():
        i = aGraph.get_node(n)
        label = n
        try:
            if graph.node[n]["nodeType"] == "transformer":
                nodeVLabel = '{0.real:.1f}/{1.real:.1f}V'.format(graph.node[n]["primaryVoltage"], graph.node[n]["secondaryVoltage2"])
                label += '\\n' + nodeVLabel
            else:
                nodeVLabel = '{0.real:.1f}V'.format(graph.node[i]["trueVoltage"])
                label += '\\n' + nodeVLabel
        except KeyError:
            pass

        try:
            pctVdrop = 100.0 * (graph.node[n]["nomVoltage"] - graph.node[n]["trueVoltage"]) / graph.node[n]["nomVoltage"]
            nodeVdLabel = '{0.real:.1f} % Drop'.format(pctVdrop)
            label += '\\n' + nodeVdLabel
        except KeyError:
            pass

        try:
            nodeSSCLabel = '{0.real:.1f} SSC_LL'.format(graph.node[n]["SSC_LL"])
            label += '\\n' + nodeSSCLabel
        except KeyError:
            pass

        n.attr['label'] = label
        aGraph.node_attr['style'] = 'filled'
        aGraph.node_attr['fillcolor'] = "#CCCCFF"
        aGraph.node_attr['fontsize'] = fontSize
        aGraph.edge_attr['fontsize'] = fontSize

    aGraph.layout(prog='dot')
    aGraph.draw(outPutPath+'/System_Render.tiff')
    # img = Image.open(dir_path+'output.png')
    # img.show()
