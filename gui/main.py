import os, platform, sys, inspect

from PyQt4.QtCore import *
from PyQt4.QtGui import *

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from calc_functions import *
from checker_functions import over_voltage_check
from plotting import *
import networkx as nx
from classes import RadialPowerSystem
from report.reports import create_report
import matplotlib.pyplot as plt


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.image = QImage()
        self.dirty = False
        self.filename = None

        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.imageLabel)

        logDockWidget = QDockWidget("Log", self)
        logDockWidget.setObjectName("LogDockWidget")
        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|
                                      Qt.RightDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)

        self.printer = None

        self.statusLabel = QLabel()
        self.statusLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.statusLabel)
        status.showMessage("Ready", 5000)

        #File menu actions
        fileNewAction = self.create_action("&New...", self.file_new,
                QKeySequence.New, "filenew", "Create new power system")
        fileOpenAction = self.create_action("&Open...", self.file_open,
                QKeySequence.Open, "fileopen",
                "Open an existing power system")
        fileSaveAction = self.create_action("&Save", self.file_save,
                QKeySequence.Save, "filesave", "Save the power system")
        fileSaveAsAction = self.create_action("Save &As...",
                self.fileSaveAs, icon="filesaveas",
                tip="Save the power system using a new name")
        filePrintAction = self.create_action("&Print", self.file_print,
                QKeySequence.Print, "fileprint", "Pring power system image")
        fileQuitAction = self.create_action("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")

        #Edit menu actions
        editAddBusAction = self.create_action("Add Bus", self.add_bus,
                "Alt+B", "addbus", "Add bus node ")
        editAddXfmrAction = self.create_action("Add Service", self.add_xfmr,
                "Alt+X", "addxfmr", "Add xfmr node")
        editAddLoadAction = self.create_action("Add Load", self.add_load,
                "Alt+L", "addload", "Add load node")
        editNodeAction = self.create_action("Edit Node", self.edit_node,
                "Alt+E", "editnode", "Edit node")

        #Report menu actions
        makeReportAction = self.create_action("&Report", self.make_report,
                "Alt+R", "makereport", "Output power system report")

        #Help menu actions
        helpAboutAction = self.create_action("&About Image Changer",
                self.helpAbout)
        helpHelpAction = self.create_action("&Help", self.helpHelp,
                QKeySequence.HelpContents)

        #Create file menu and add actions
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewAction, fileOpenAction,
                fileSaveAction, fileSaveAsAction, None,
                filePrintAction, fileQuitAction)
        self.connect(self.fileMenu, SIGNAL("aboutToShow()"),
                     self.update_file_menu)

        #Create report menu and add actions
        reportMenu = self.menuBar().addMenu("&Report")
        self.add_actions(reportMenu, (makeReportAction))

        #Create edit menu
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editAddLoadAction, editAddBusAction,
                editAddXfmrAction, editAddServiceAction))

        #Add file, edit, report toolbars for quick access
        fileToolBar = self.addToolBar("File")
        fileToolbar = setObjectName("FileToolBar")
        self.add_actions(fileToolbar, (fileNewAction, fileOpenAction,
                fileSaveAction, fileSaveAsAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar = setObjectName("EditToolBar")
        self.add_actions(editToolbar, (editAddLoadAction, editAddBusAction,
                editAddXfmrAction, editAddServiceAction))

        #Add actions for status updates on system edits
        self.add_actions(self.statusLabel, (editAddLoadAction, editAddBusAction,
                editAddXfmrAction, editAddServiceAction))

        #Tracking of recent power system input files accessed
        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles").toStringList()

        #Maintain apperance settings and restore upon opening
        size = settings.value("MainWindow/Size",
                              QVariant(QSize(600, 500))).toSize()
        self.resize(size)
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())

        #Main window title
        self.setWindowTitle("DiGraph Power Calculations")

        #Update for recently accessed files
        self.updateFileMenu()
        QTimer.singleShot(0, self.loadInitialFile)


        def create_action(self, text, slot=None, shortcut=None, icon=None,
                         tip=None, signal="triggered()"):
            action = QAction(text, self)
            if icon is not None:
                action.setIcon(QIson(":{}.png".format(icon)))
            if shortcut is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            if slot is not None:
                self.connect(action, SIGNAL(signal), slot)
            return action


        def add_actions(self, target, actions):
            for action in actions:
                if action is None:
                    target.addSeparator()
                else:
                    target.addAction(action)


        def closeEvent(self, event):
            if self.okToContinue():
                settings = QSettings()
                filename = QVariant(QString(self.filename)) \
                        if self.filename is not None else QVariant()
                settings.setValue("LastFile", filename)
                recentFiles = QVariant(self.recentFiles) \
                        if self.recentFiles else QVariant()
                settings.setValue("RecentFiles", recentFiles)
                settings.setValue("MainWindow/Size", QVariant(self.size()))
                settings.setValue("MainWindow/Position",
                        QVariant(self.pos()))
                settings.setValue("MainWindow/State",
                        QVariant(self.saveState()))
            else:
                event.ignore()


        def okToContinue(self):
            if self.dirty:
                reply = QMessageBox.question(self,
                                "DiGraph Power Calculations - Unsaved Changes",
                                "Save unsaved changes?",
                                QMessageBox.Yes|QMessageBox.No|
                                QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return False
                elif reply == QMessageBox.Yes:
                    self.fileSave()
            return True


        def loadInitialFile(self):
            settings = QSettings()
            fname = unicode(settings.value("LastFile").toString())
            if fname and QFile.exists(fname):
                self.loadFile(fname)


    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        self.listWidget.addItem(message)
        if self.filename is not None:
            self.setWindowTitle("DiGraph Power Calculations - {}[*]"
                                .format(os.path.basename(self.filename)))
        elif not self.image.isNull():
            self.setWindowTitle("DiGraph Power Calculations - Unnamed[*]")
        else:
            self.setWindowTitle("DiGraph Power Calculations[*]")
        self.setWindowModified(self.dirty)


    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        if self.filename is not None:
            current = QString(self.filename)
        else:
            None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon(":/icon.png"),
                                "&{0} {1}".format(i+1, QFileInfo(fname).fileName()),
                                self)
                action.setData(QVariant(fname))
                self.connection(action, SIGNAL("triggered()"),
                                self.loadFile)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])


    def fileNew(self):
        if not self.okToContinue():
            return
    # TODO: Create newsystemdlg module with NewSystemDlg class,
    # must include system name as init variable and create a service node
        dialog = newsystemdlg.NewSystemDlg(self)
        if dialog.exec_():
            self.addRecentFile(self.filename)
            self.image = QImage()
            self.image = dialog.image()
            #TODO: Create image when initalizing system, will be only service node
            #at first. Store image path in dialog class so it can be accessed






def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Alex Mims")
    app.setOrganizationDomain("N/A")
    app.setApplicationName("DiGraph Power Calculations")
    app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()


main()
