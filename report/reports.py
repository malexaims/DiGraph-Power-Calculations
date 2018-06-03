import networkx as nx
import os,sys,inspect
from datetime import datetime
from appy.pod.renderer import Renderer
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import calc_functions
from classes import RadialPowerSystem

# outPutPath+'/{0}_Plot_{1}.tiff'.format(graph.name, datetime.now().strftime("%Y-%m-%d"))

def create_report(graph, outPutPath=None, templateName="reportTemplate.ods"):

    systemName = graph.name

    dataDicts = []
    for beg, end, data in graph.edges(data=True):
        edgeDict = {'from':beg, 'to':end, 'length':data['length']}
        dataDicts.append(edgeDict)

    if outPutPath == None:
        raise Exception("OutPutPath not set")
        outPutPath = outPutPath+'/{0}+Report_{1}.odt'.format(graph.name, datetime.now().strftime("%Y-%m-%d"))
    outPutPath = outPutPath+'/{0}+Report_{1}.odt'.format(graph.name, datetime.now().strftime("%Y-%m-%d"))

    renderer = Renderer(currentdir+'/'+templateName, locals(), outPutPath)
    renderer.run()
