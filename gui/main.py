import os, platform, sys, inspect, re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from calc_functions import *
from checker_functions import over_voltage_check
from plotting import draw_graph
import networkx as nx
from classes import RadialPowerSystem
from report.reports import create_report
import matplotlib.pyplot as plt
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)
import newsystemdlg

__version__ = "1.0.0"

#TODO: Make icons for buttons. Rename as needed to fit MainWindow

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.imagefilename = None
        self.graph = None

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
                self.file_save_as, icon="filesaveas",
                tip="Save the power system using a new name")
        filePrintAction = self.create_action("&Print", self.file_print,
                QKeySequence.Print, "fileprint", "Pring power system image")
        fileQuitAction = self.create_action("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")

        #Edit menu actions
        editAddBusAction = self.create_action("Add Bus", self.add_bus,
                "Alt+B", "addbus", "Add bus node ")
        editAddXfmrAction = self.create_action("Add Transformer", self.add_xfmr,
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
                self.help_about)
        helpHelpAction = self.create_action("&Help", self.help_Help,
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
        reportMenu.addAction(makeReportAction)

        #Create edit menu
        editMenu = self.menuBar().addMenu("&Edit")
        self.add_actions(editMenu, (editAddLoadAction, editAddBusAction,
                         editAddXfmrAction, editNodeAction))

        #Add file, edit, report toolbars for quick access
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.add_actions(fileToolbar, (fileNewAction, fileOpenAction,
                         fileSaveAction, fileSaveAsAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.add_actions(editToolbar, (editAddLoadAction, editAddBusAction,
                         editAddXfmrAction, editNodeAction))

        #Add actions for status updates on system edits
        self.add_actions(self.statusLabel, (editAddLoadAction, editAddBusAction,
                         editAddXfmrAction, editNodeAction))

        #Tracking of recent power system input files accessed
        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles").toStringList()

        #Maintain apperance settings and restore upon opening
        size = settings.value("MainWindow/Size",
                              QVariant(QSize(600, 500))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position",
                                  QVariant(QPoint(0, 0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())

        #Main window title
        self.setWindowTitle("DiGraph Power Calculations")

        #Update for recently accessed files
        self.update_file_menu()
        QTimer.singleShot(0, self.loadInitialFile)


    def create_action(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":{}.png".format(icon)))
        if shortcut is not None:
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


    def close_event(self, event):
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


    def update_status(self, message):
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


    def update_file_menu(self):
        self.fileMenu.clear()
        self.add_actions(self.fileMenu, self.fileMenuActions[:-1])
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


    def file_new(self):
        if not self.okToContinue():
            return
        dialog = newsystemdlg.NewSystemDlg(self)
        if dialog.exec_():
            self.add_recent_file(self.filename)
            name, props = dialog.get_service_properties()
            self.graph = RadialPowerSystem(dialog.get_system_name()) #Create power system
            self.graph.add_node(name, **props) #Add the service node
            self.file_save_as() #Sets self.filename and self.imagefilename
            image = draw_graph(self.graph, outPutPath=str(self.imagefilename))
            self.image = QImage(self.imagefilename)
            self.show_image()
            self.statusLabel.setText("New system created.")
            self.update_status("Created new power system.")


    def file_open(self):
        if not self.okToContinue():
            return
        if self.filename is not None:
            dir = os.path.dirname(self.filename)
        else:
            None
        fname = unicode(QFileDialog.getOpenFileName(self,
                        "DiGraph Power Calcs - Choose File",
                        dir, "Graph files (.gpickle)" ))
        if fname:
            self.load_file(fname)


    def load_file(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = unicode(action.data().toString())
                if not self.okToContinue():
                    return
            else:
                return
            if fname:
                self.filename = None
                graph = None
                try:
                    self.graph = nx.read_gpickle(fname)
                    self.add_recent_file(fname)
                    self.filename = fname
                    self.get_image() #TODO: Write image setter function for files upon loading
                    self.show_image()
                    self.dirty = False
                    message = "Loaded {}".format(os.path.basename(fname))
                    self.update_status(message)
                except Exception:
                    message = "Failed to read {}".format(fname)


    def add_recent_file(self, fname):
        if fname is None:
            return
        if not self.recentFiles.contains(fname):
            self.recentFiles.prepend(QString(fname))
            while self.recentFiles.count() > 9:
                self.recentFiles.takeLast()


    def file_save(self):
        if self.graph is None:
            return
        if self.filename is None:
            self.file_save_as()
        else:
            try:
                nx.write_gpickle(self.graph, self.filename)
                self.update_status("Saved as {}".format(self.filename))
                self.dirty = False
            except Exception:
                self.update_status("Failed to save {}".format(self.filename))


    def file_save_as(self):
        if self.graph is None:
            return
        if self.filename is not None:
            fname = self.filename
        else:
            fname = ".gpickle"
        fname = unicode(QFileDialog.getSaveFileName(self,
                        "DiGraph Power Calcs - Save System",
                        fname, "Graph files (.gpickle)"))
        if fname:
            if "." not in fname:
                fname += ".gpickle"
            imagefilename = fname
            self.imagefilename = re.sub("\.gpickle$", ".png", imagefilename)
            self.add_recent_file(fname)
            self.filename = fname
            self.file_save()


    def file_print(self):
        if self.image.isNull():
            self.update_status("Printing failed. No image to print")
            return
        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer = setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.drawImage(0, 0, self.image)
            self.update_status("Printed {}".format(self.filename))

#NOTE: Is a check required to assess if all inputs were entered for nodes here or in dialog

    def add_bus(self):
        if self.graph is None:
            return
        dialog = editdlg.AddBus(self.graph, self) #TODO: Make editdlg module with AddBus class
        if dialog.exec_():
            attrs = dialog.attribues()
            self.graph.add_node(dialog.name(), **attrs)
            self.show_image()
            self.dirty = True
            self.update_status("Added bus {}".format(dialog.name()))


    def add_xfmr(self):
        if self.graph is None:
            return
        dialog = editdlg.AddXfmr(self.graph, self)
        if dialog.exec_():
            attrs = dialog.attribues()
            self.graph.add_node(dialog.name(), **attrs)
            self.show_image()
            self.dirty = True
            self.update_status("Added xfmr {}".format(dialog.name()))


    def add_load(self):
        if self.graph is None:
            return
        dialog = editdlg.AddLoad(self.graph, self)
        if dialog.exec_():
            attrs = dialog.attribues()
            self.graph.add_node(dialog.name(), **attrs)
            self.show_image()
            self.dirty = True
            self.update_status("Added load {}".format(dialog.name()))


    def edit_node(self):
        if self.graph is None:
            return
        dialog = editdlg.EditNode(self.graph, self)
        if dialog.exec_():
            editNode = dialog.editedNode()
            edditedAttrs = dialog.editedAttrs()
            attrs = {editNode: edditedAttrs} #Dict of name: value for edited attrs
            nx.set_node_attributes(self.graph, attrs)
            self.show_image()
            self.dirty = True
            self.update_status("Edited node {}".format(editNode))


    def make_report(self):
        if self.graph is None:
            return
        dialog = reportdlg.MakeReport(self.graph, self)
        if dialog.exec_():
            outPutPath = dialog.outPutPath()
            plotting = dialog.plotting()
            create_report(self.graph,
                          outPutPath=outPutPath,
                          plotting=plotting)
            self.update_status("Made report {}".format(outPutPath))


    def show_image(self, parent=None):
        if self.image.isNull():
            return
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))


    def help_about(self):
        QMessageBox.about(self, "About DiGraph Power Calculations",
                """<b>DiGraph Power Calculations</b> v {}
                <p>This application can be used to perform
                basic radial power system calculations.
                <p>Python {} - Qt {} - PyQt {} on {}""".format(
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))


    def help_Help(self):
        form = helpform.HelpForm("index.html", self) #TODO: Edit help html form
        form.show()



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
