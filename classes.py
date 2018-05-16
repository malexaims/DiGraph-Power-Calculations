from networkx import DiGraph
import constants
import math
import pandas as pd


class RadialPowerSystem(DiGraph):
    """
    Class representation of a radial power distribution system. Main purpose
    is to permit creation easier creation of a DiGraph representation of a
    radial power system."""


    def __init__(self):
        super(RadialPowerSystem, self).__init__()


    def add_connection(self, begNode, endNode, wireSize=None, wireMat='copper', conduitMat=None, length=None):
        """Creates edge between two nodes representing a wire connection.

        Parameters
        ----------
        begNode = string of beginning node name (closest to source)
        endNode = string of ending node name (furthest from source)
        wireSize = AWG (14 - 4/0) or kcmil (250 - 400) of wire
        wireMaterial = conductor material: copper or aluminum
        conduitMat = conduit material (PVC, aluminum, steel)
        length = wire length between nodes in feet

        Output
        ------
        A DiGraph edge between begNode and endNode with xL, rL, and length weight attributes.
        xL = reactance in ohms per 1000ft
        rL = resistance in ohms per 1000 ft
        length = wire length between bedNode and endNode in feet
        """

        conductorDataCopper = constants.conductorDataCopper
        conductorDataAlum = constants.conductorDataAlum

        try:
            wireSize = str(wireSize)
            if wireSize not in constants.compatWireSizes:
                raise ValueError("Incorrect wire size '{}' or wire size not supported.".format(wireSize))
        except TypeError:
            print "Wire size must be a string. Entry:", wireSize

        try:
            wireMat = str(wireMat)
            if wireMat not in constants.compatWireMaterial:
                raise ValueError("Incorrect wire material '{}' or wire material not supported.".format(wireMat))
        except TypeError:
            print "Wire material must be a string. Entry:", wireMat

        try:
            conduitMat = str(conduitMat)
            if conduitMat not in constants.compatConduitMaterial:
                raise ValueError("Incorrect conduit material '{}' or conduit material not supported.".format(conduitMat))
        except TypeError:
            "Conduit type must be a string. Entry:", conduitType

        try:
            length = float(length)
        except TypeError:
            "Incorrect connection length entry. Entry:", length
        if length < 0:
            raise ValueError("Length must be positive. Between {1} and {2}.".format(begNode, endNode))

        if wireMat == "aluminum":
            wireDataDict = conductorDataAlum
        else:
            wireDataDict = conductorDataCopper

        if conduitMat in ["HDPE", "PVC", "aluminum"]:
            reactDict = "xL NF"
        else:
            reactDict = "xL F"

        if conduitMat in ["HDPE", "PVC"]:
            resistDict = "xR PVC"
        if conduitMat == "aluminum":
            resistDict = "xR Alum"
        else:
            resistDict = "xR Steel"

        #Get the reactance and resistance of the wire based on wire and conduit material entered
        xL = wireDataDict[reactDict].get(wireSize)
        rL = wireDataDict[resistDict].get(wireSize)
        #Create a edge with appropriate attributes
        self.add_edge(begNode, endNode, xL=xL, rL=rL, length=length)
