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
from helper_functions import get_node_voltage


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
        edge.attr['label'] = '{0:.2f} A \\n {1} ft \\n {2} AWG'.format(
                              graph[edge[0]][edge[1]]["I"].real,
                              graph[edge[0]][edge[1]]["length"],
                              graph[edge[0]][edge[1]]["wireSize"])
        # edge.attr['label'] = '{0:.2f}A \\n {1}ft'.format(
        #                       graph[edge[0]][edge[1]]["I"].real,
        #                       graph[edge[0]][edge[1]]["length"])
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
            if graph.node[n]["nodeType"] == "transformer":
                raise KeyError
            pctVdrop = 100.0 * (get_node_voltage(graph, n) - graph.node[n]["trueVoltage"]) / get_node_voltage(graph, n)
            nodeVdLabel = '{0.real:.1f} % Drop'.format(pctVdrop)
            label += '\\n' + nodeVdLabel
        except KeyError:
            pass

        try:
            nodeSSCLLLabel = '{0.real:.1f} SSC_LL'.format(graph.node[n]["SSC_LL"])
            label += '\\n' + nodeSSCLLLabel
        except KeyError:
            pass

        try:
            nodeSSCLNLabel = '{0.real:.1f} SSC_LN'.format(graph.node[n]["SSC_LN"])
            label += '\\n' + nodeSSCLNLabel
        except KeyError:
            pass

        n.attr['label'] = label
        aGraph.node_attr['style'] = 'filled'
        aGraph.node_attr['fillcolor'] = "#CCCCFF"
        aGraph.node_attr['fontsize'] = fontSize
        aGraph.edge_attr['fontsize'] = fontSize

    aGraph.layout(prog='dot')
    aGraph.draw(outPutPath+'/System_Render.tiff')
    # img = Image.open(outPutPath+'/System_Render.tiff')
    # img.show()
