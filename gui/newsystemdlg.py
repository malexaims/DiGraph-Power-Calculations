import sys, os, inspect
from PyQt4.QtCore import *
from PyQt4.QtGui import *
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from classes import RadialPowerSystem
from constants import voltageCompatDict


class NewSystemDlg(QDialog):

    def __init__(self, parent=None):
        super(NewSystemDlg, self).__init__(parent)

        diaTitle = "&New Sytem"
        nameLabel = "&Name of New System"

        self.systemName, ok = QInputDialog.getText(self, nameLabel, nameLabel)
        if ok and len(str(self.systemName)) > 0:
            self.makeService()

#TODO: Incorporate setValidator to entries based on program capabilities
    def makeService(self):
            self.nodeType = "service"

            nameLabel = QLabel("Service Node Name")
            self.nodeName = QLineEdit("")
            nameLabel.setBuddy(self.nodeName)

            nomVLLLabel = QLabel("L-L Voltage")
            self.nomVLL = QLineEdit("240")
            nomVLLLabel.setBuddy(self.nomVLL)

            nomVLNLabel = QLabel("L-N Voltage")
            self.nomVLN = QLineEdit("120")
            nomVLLLabel.setBuddy(self.nomVLN)

            phaseLabel = QLabel("Phase (1 or 3)")
            self.phase = QLineEdit("1")
            phaseLabel.setBuddy(self.phase)

            sscLabel = QLabel("SSC Available")
            self.ssc = QLineEdit("0")
            sscLabel.setBuddy(self.ssc)

            xRLabel = QLabel("X/R Ratio")
            self.xRRatio = QLineEdit("10")
            xRLabel.setBuddy(self.xRRatio)

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)

            grid = QGridLayout()
            grid.addWidget(nameLabel, 0, 0)
            grid.addWidget(self.nodeName, 0, 1)
            grid.addWidget(nomVLLLabel, 1, 0)
            grid.addWidget(self.nomVLL, 1, 1)
            grid.addWidget(nomVLNLabel, 2, 0)
            grid.addWidget(self.nomVLN, 2, 1)
            grid.addWidget(phaseLabel, 3, 0)
            grid.addWidget(self.phase, 3, 1)
            grid.addWidget(sscLabel, 4, 0)
            grid.addWidget(self.ssc, 4, 1)
            grid.addWidget(xRLabel, 5, 0)
            grid.addWidget(self.xRRatio, 5, 1)
            grid.addWidget(buttonBox, 6, 0)
            self.setLayout(grid)

            self.connect(buttonBox, SIGNAL("accepted()"),
                         self, SLOT("accept()"))
            self.connect(buttonBox, SIGNAL("rejected()"),
                         self, SLOT("reject()"))
            self.nodeName.selectAll()
            self.nodeName.setFocus()
            self.setWindowTitle("Service Node Properties")

    def accept(self):
        class NameError(Exception): pass
        class VLLError(Exception): pass
        class VLNError(Exception): pass
        class PhaseError(Exception): pass
        class SSCError(Exception): pass
        class XRError(Exception): pass

        name = unicode(self.nodeName.text())
        vLL = unicode(self.nomVLL.text())
        vLN = unicode(self.nomVLN.text())
        phase = unicode(self.phase.text())
        ssc = unicode(self.ssc.text())
        xR = unicode(self.xRRatio.text())

        try:
            if len(name) == 0:
                raise NameError, ("Name may not be empty.")

            if vLL not in voltageCompatDict.keys():
                raise VLLError, ("""Invalid L-L Voltage.
                                      Must be one of the following {}"""
                                      .format(voltageCompatDict.keys()))

            if float(vLN) not in voltageCompatDict[vLL]:
                raise VLNError, ("""L-N Voltage not compatible with L-L Voltage.
                                     Must be one of the following {}"""
                                     .format(voltageCompatDict[vLL]))

            if phase not in ["1", "3"]:
                raise PhaseError, ("""Phase must be 1 or 3.""")

            if float(ssc) < 0:
                raise SSCError, ("SSC must be positive.")

            if float(xR) < 0:
                raise XRError, ("X/R Ratio must be positive.")

        except NameError, e:
            QMessageBox.warning(self, "Name Error", unicode(e))
            self.nodeName.selectAll()
            self.nodeName.setFocus()
            return

        except VLLError, e:
            QMessageBox.warning(self, "L-L Voltage Errror", unicode(e))
            self.nomVLL.selectAll()
            self.nomVLL.setFocus()
            return

        except VLNError, e:
            QMessageBox.warning(self, "L-N Voltage Error", unicode(e))
            self.nomVLN.selectAll()
            self.nomVLN.setFocus()
            return

        except PhaseError, e:
            QMessageBox.warning(self, "Phase Error", unicode(e))
            self.phase.selectAll()
            self.phase.setFocus()
            return

        except SSCError, e:
            QMessageBox.warning(self, "SSC Error", unicode(e))
            self.ssc.selectAll()
            self.phase.setFocus()
            return

        except XRError, e:
            QMessageBox.warning(self, "X/R Ratio Error", unicode(e))
            self.xRRatio.selectAll()
            self.xRRatio.setFocus()
            return

        QDialog.accept(self)


    def get_system_name(self):
         return str(self.systemName)


    def get_service_properties(self):
        props = dict(nodeType=self.nodeType,
                 nomVLL=self.nomVLL,
                 nomVLN=self.nomVLN,
                 phase=self.phase,
                 availSSC=self.ssc,
                 xRRatio=self.xRRatio)
        return self.nodeName.text(), props



if __name__ == "__main__":

    app = QApplication(sys.argv)
    form = NewSystemDlg()
    form.show()
    app.exec_()
