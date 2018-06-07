import networkx as nx
import math
import os,sys,inspect
from datetime import datetime
from appy.pod.renderer import Renderer
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import calc_functions
from helper_functions import get_node_voltage
from classes import RadialPowerSystem



def create_report(graph, outPutPath=None, templateName="reportTemplate.ods"):

    systemName = graph.name
    dateTime = '{}'.format(datetime.now())

    edgeData = []
    for beg, end, data in graph.edges(data=True):
        vDrop = '{0.real:.1f}'.format(data['vDrop'])
        I = '{0.real:.1f}'.format(data['I'])
        edgeDict = {'from':beg, 'to':end, 'length':data['length'], 'I':I, 'vDrop':vDrop,
                    'wireSize':data['wireSize'], 'numWires':data['numWires'], 'Ifloat': data['I']}
        edgeData.append(edgeDict)

    nodeData = []
    for n, data in graph.nodes(data=True):
        nodeDict = {}
        if data['nodeType'] == 'transformer':
            nomVoltage = data['nomPrimaryV']
            trueVoltage = '{0.real:.1f}'.format(data['primaryVoltage'])
            pctVdrop = '--'
            pctVdropFloat = 0.0
        else:
            nomVoltage = get_node_voltage(graph, n)
            trueVoltage = data["trueVoltage"]
            pctVdropFloat = 100.0 * (nomVoltage - trueVoltage) / nomVoltage
            pctVdrop = '{0.real:.1f}'.format(pctVdropFloat)
            trueVoltage = '{0.real:.1f}'.format(trueVoltage)

        nodeDict = {'name':n, 'nomVoltage':nomVoltage, 'trueVoltage':trueVoltage,
                    'pctVdrop':pctVdrop, 'dateTime':dateTime, 'pctVdropFloat': pctVdropFloat}

        try:
            kVA = math.sqrt(data['w']**2 + data['vAr'])/1000.0
            nodeDict['kVA'] = kVA
        except KeyError:
            nodeDict['kVA'] = '--'

        try:
            nodeDict['SSC_LL'] = '{0.real:.1f}'.format(data['SSC_LL'])
        except KeyError:
            nodeDict['SSC_LL'] = '--'
            pass
        try:
            nodeDict['SSC_LN'] = '{0.real:.1f}'.format(data['SSC_LN'])
        except KeyError:
            nodeDict['SSC_LN'] = '--'
            pass

        nodeData.append(nodeDict)

    edgeData = sorted(edgeData[:], key=lambda k: k['Ifloat'].real, reverse=True)
    nodeData = sorted(nodeData[:], key=lambda k: k['pctVdropFloat'].real, reverse=True)

    if outPutPath == None:
        raise Exception("OutPutPath not set")
        outPutPath = outPutPath+'/{0}_Report_{1}.odt'.format(graph.name, datetime.now().strftime("%Y-%m-%d"))
    outPutPath = outPutPath+'/{0}_Report_{1}.odt'.format(graph.name, datetime.now().strftime("%Y-%m-%d"))

    renderer = Renderer(currentdir+'/'+templateName, locals(), outPutPath)
    renderer.run()
