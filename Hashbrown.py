# Hashbrown by KeyboardCombination 2022
# rbxdl by Modnark

# Init:
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import subprocess

# Config:
Dir = "Downloaded"
SaveInFolder = True
CurrentProcess = None

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hashbrown")
        self.setWindowIcon(QtGui.QIcon('icon/HashbrownLogo.png'))
        self.setFixedSize(640, 164)

        self.InitMainUI()
        self.MenubarInit()
        self.SettingsMenuInit()
        self.AboutMenuInit()

        self.Process = None

    def InitMainUI(self):
        self.AssetInput = QtWidgets.QLineEdit(self)
        self.AssetInput.setGeometry(224, 32, 192, 32)
        self.AssetInput.setAlignment(QtCore.Qt.AlignCenter)
        self.AssetInput.setPlaceholderText("Insert Asset ID")

        self.VersionInput = QtWidgets.QSpinBox(self)
        # self.VersionInput.setMaximum(2048)
        self.VersionInput.setGeometry(420, 36, 80, 28)

        self.DownloadAllVersions = QtWidgets.QCheckBox(self)
        self.DownloadAllVersions.setText("Download all versions")
        self.DownloadAllVersions.setGeometry(256, 64, 256, 24)

        self.DownloadAllVersions.clicked.connect(self.ToggleDownloadAllVersions)

        self.DownloadButton = QtWidgets.QPushButton("Download", self)
        self.DownloadButton.setGeometry(256, 96, 128, 32)

        self.DownloadButton.clicked.connect(self.InitializeDownload)
        
        self.ProgressBar = QtWidgets.QProgressBar(self)
        self.ProgressBar.setGeometry(192, 132, 256, 24)

    def SettingsMenuInit(self):
        self.SettingsWidget = QtWidgets.QWidget()
        self.SettingsWidget.setWindowTitle("Settings")
        self.SettingsWidget.setWindowIcon(QtGui.QIcon('icon/HashbrownLogo.png'))
        self.SettingsWidget.setFixedSize(232, 104)
        self.SettingsWidget.setStyleSheet(open("style/style.qss").read())

        #Directory setting:
        self.DirectoryInputText = QtWidgets.QLabel(self.SettingsWidget)
        self.DirectoryInputText.setText("Directory: ")
        self.DirectoryInputText.setGeometry(8, 8, 128, 16)

        self.DirectoryInput = QtWidgets.QFileDialog(self.SettingsWidget)
        self.DirectoryInput.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)

        self.DirectoryStringInput = QtWidgets.QLineEdit(self.SettingsWidget)
        self.DirectoryStringInput.setGeometry(72, 4, 128, 24)

        self.SelectDirectoryButton = QtWidgets.QPushButton(self.SettingsWidget)
        self.SelectDirectoryButton.setGeometry(204, 4, 24, 24)
        self.SelectDirectoryButton.setText("...")

        self.SelectDirectoryButton.clicked.connect(self.SetDirectory)
        
        #Save asset in directory setting:
        self.SaveInFolderOption = QtWidgets.QCheckBox(self.SettingsWidget)
        self.SaveInFolderOption.setText("Save place in folder")
        self.SaveInFolderOption.setGeometry(49, 32, 134, 24)

        #Apply settings button:
        ApplyButton = QtWidgets.QPushButton(self.SettingsWidget)
        ApplyButton.setText("Apply")
        ApplyButton.setGeometry(68, 64, 96, 32)

        ApplyButton.clicked.connect(self.ApplySettings)
    
    def ApplySettings(self):
        global Dir
        global SaveInFolder

        Dir = self.DirectoryStringInput.text()
        SaveInFolder = self.SaveInFolderOption.isChecked()

    def SetDirectory(self):
        SelectedDirectory = self.DirectoryInput.getExistingDirectory()
        self.DirectoryStringInput.setText(SelectedDirectory)

    def ToggleDownloadAllVersions(self):
        self.VersionInput.setEnabled(not self.DownloadAllVersions.isChecked())

    def closeEvent(self, event):
        if (self.Process != None):
            self.Process.terminate()

    def InitializeDownload(self):
        if (self.AssetInput.text() == ""):
            QtWidgets.QMessageBox.critical(MainWidget(), "Error!", "Please enter an ID!")
            return

        Widget.ProgressBar.setMaximum(0)
        Widget.AssetInput.setEnabled(False)
        Widget.VersionInput.setEnabled(False)
        Widget.DownloadButton.setEnabled(False)

        if (self.DownloadAllVersions.isChecked()):
            if (SaveInFolder):
                self.Process = subprocess.Popen(['python', 'rbxdl.py', 'single', f'{self.AssetInput.text()}', f'--allVer', f'--sdirs', f'--dir', Dir])
            else:
                self.Process = subprocess.Popen(['python', 'rbxdl.py', 'single', f'{self.AssetInput.text()}', f'--allVer', f'--dir', Dir])
        else:
            if (SaveInFolder):
                self.Process = subprocess.Popen(['python', 'rbxdl.py', 'single', f'{self.AssetInput.text()}', f'--ver', str(self.VersionInput.value()), f'--sdirs', f'--dir', Dir])
            else:
                self.Process = subprocess.Popen(['python', 'rbxdl.py', 'single', f'{self.AssetInput.text()}', f'--ver', str(self.VersionInput.value()), f'--dir', Dir])
        
        while (self.Process.poll() is None):
            QtWidgets.QApplication.processEvents()

        if (self.Process.returncode != 0):
            QtWidgets.QMessageBox.critical(MainWidget(), "Error!", "An error occured while downloading!")
        else:
            QtWidgets.QMessageBox.information(MainWidget(), "Success!", "Download finished!")

        Widget.ProgressBar.setMaximum(100)
        Widget.AssetInput.setEnabled(True)
        Widget.VersionInput.setEnabled(True)
        Widget.DownloadButton.setEnabled(True)

    def ShowSettingsMenu(self):
        self.DirectoryStringInput.setText(Dir)
        self.SaveInFolderOption.setChecked(SaveInFolder)
        # self.SaveInFolderOption.setChecked(SaveInFolder)
        self.SettingsWidget.show()

    def AboutMenuInit(self):
        self.AboutWidget = QtWidgets.QWidget()
        self.AboutWidget.setWindowTitle("About")
        self.AboutWidget.setFixedSize(256, 142)
        self.AboutWidget.setWindowIcon(QtGui.QIcon('icon/HashbrownLogo.png'))
        self.AboutWidget.setStyleSheet(open("style/style.qss").read())

        #Create an image of the Hashbrown logo:
        self.Logo = QtWidgets.QLabel(self.AboutWidget, alignment=QtCore.Qt.AlignCenter)
        self.Logo.setGeometry(0, 0, 256, 96)
        
        #Create pixmap of the logo:
        self.LogoImage = QtGui.QImage("icon/HashbrownLogo.png")
        self.LogoPixmap = QtGui.QPixmap(self.LogoImage.scaled(96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.Logo.setPixmap(self.LogoPixmap)

        ProgramName = QtWidgets.QLabel("Hashbrown", alignment=QtCore.Qt.AlignCenter)
        ProgramName.setGeometry(0, 96, 256, 16)
        ProgramName.setParent(self.AboutWidget)
        ProgramName.setStyleSheet("font-weight: 500; font-size: 16px;")

        AboutText = QtWidgets.QLabel("KeyboardCombination 2022", alignment=QtCore.Qt.AlignCenter)
        AboutText.setGeometry(0, 120, 256, 16)
        AboutText.setParent(self.AboutWidget)

    def ShowAboutMenu(self):
        self.AboutWidget.show()

    def MenubarInit(self):
        #Menubar:
        Menubar = self.menuBar()

        #Tools Tab:
        SettingsAction = QtGui.QAction("&Settings", self)
        SettingsAction.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        SettingsAction.triggered.connect(self.ShowSettingsMenu)

        QuitAction = QtGui.QAction("&Quit", self)
        QuitAction.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        QuitAction.triggered.connect(self.close)

        ToolsMenu = Menubar.addMenu("&Tools")
        ToolsMenu.addAction(SettingsAction)
        ToolsMenu.addAction(QuitAction)

        #Help Tab:
        AboutAction = QtGui.QAction("&About", self)
        AboutAction.triggered.connect(self.ShowAboutMenu)

        HelpMenu = Menubar.addMenu("&Help")
        HelpMenu.addAction(AboutAction)

# Hookup:
if (__name__ == "__main__"):
    HashbrownApp = QtWidgets.QApplication([])

    Widget = MainWidget()
    Widget.resize(640, 480)
    Widget.show()

    #Font:
    QtGui.QFontDatabase.addApplicationFont("style/fonts/Rubik.ttf")

    #Styling:
    Widget.setStyleSheet(open("style/style.qss").read())

    sys.exit(HashbrownApp.exec())