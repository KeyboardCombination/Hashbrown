# Hashbrown by KeyboardCombination 2022
# Original downloader by Lannuked

# Init:
import sys
from tkinter import Menu
from PySide6 import QtCore, QtWidgets, QtGui
import PySide6
import requests
import re
import os
import time
import json
import threading
import signal

# Global Variables:
headersIn = {'User-Agent': 'Roblox/WinINet'}
assetUrl = "https://assetdelivery.roblox.com/v1/asset/?id="
CanDownloadMetadata = True

# Classes:
class AssetDownloader(QtCore.QThread):
    ThumbnailSize = "768x432"
    ThumbnailSizes = ["768x432", "576x324", "480x270", "384x216", "256x144"]

    IconSize = "512x512"
    IconSizes = ["50x50", "128x128", "150x150", "256x256", "512x512"]

    AssetSize = "512x512"
    AssetSizes = ["30x30", "42x42", "50x50", "60x62", "75x75", "110x110", "140x140", "150x150", "160x100", "160x600", "250x250", "256x144", "300x250", "304x166", "384x216", "396x216", "420x420", "480x270", "512x512", "576x324", "700x700", "728x90", "768x432"]

    #BEGIN-AssetTypeIDs
    idk = "Unknown"
    #assetTypeId = place in table
    assetTypeList = ["Image", "TShirt", "Audio", "Mesh", "Lua", "HTML", "Text",
    "Hat", "Place", "Model", "Shirt", "Pants", "Decal", idk, idk, idk, "Avatar","Head", "Face", "Gear",
    idk, idk, "Badge", "GroupEmblem", idk, "Animation", "Arms", "Legs", "Torso", "RightArm", "LeftArm",
    "LeftLeg", "RightLeg", "Package", "YouTubeVideo", "GamePass", "App", idk, "Code", "Plugin",
    "SolidModel", "MeshPart", "HairAccessory", "NeckAccessory", "ShoulderAccessory", "FrontAccessory",
    "BackAccessory", "WaistAccessory", "ClimbAnimation", "DeathAnimation", "FallAnimation",
    "IdleAnimation", "JumpAnimation", "RunAnimation", "SwimAnimation", "WalkAnimation", "PoseAnimation",
    "EarAccessory", "EyeAccessory", "LocalizationTableManifest", "LocalizationTableTranslation",
    "EmoteAnimation", "Video", "TexturePack", "TShirtAccessory", "ShirtAccessory", "PantsAccessory",
    "JacketAccessory", "SweaterAccessory", "ShortsAccessory", "LeftShoeAccessory", "RightShoeAccessory",
    "DressSkirtAccessory"]

    def fixBadStr(inputStr):
        badChars = ['"', ":"]
        goodChars = ["'", "-"]

        outputString = re.sub("[*/\\\\<>?|]", '', inputStr)
        for i in range(len(badChars)):
            outputString = outputString.replace(badChars[i], goodChars[i])
        return outputString

    def DownloadMetadata(AssetID, headers):
        dlAssetMetadata = requests.get(f'http://api.roblox.com/Marketplace/ProductInfo?assetId={AssetID}')

        if (dlAssetMetadata.status_code != 200):
            return None

        return dlAssetMetadata

    def DownloadAssetIcon(AssetID, Resolution):
        ThumbnailRequest = requests.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={AssetID}&size={Resolution}&format=Png&isCircular=false")

        if (ThumbnailRequest.status_code != 200):
            return None
        
        ThumbnailRequestJson = ThumbnailRequest.json()

        return ThumbnailRequestJson["data"][0]["imageUrl"]

    def DownloadThumbnails(AssetID, ThumbnailResolution, IconResolution):
        
        GetUniverseID = requests.get(f"https://api.roblox.com/universes/get-universe-containing-place?placeid={AssetID}")

        if (GetUniverseID.status_code != 200):
            return None, None

        UniverseID = GetUniverseID.json()["UniverseId"]

        ThumbnailRequest = requests.get(f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={UniverseID}&countPerUniverse=999999&size={ThumbnailResolution}&format=Png&isCircular=false")
        IconRequest = requests.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={UniverseID}&size={IconResolution}&format=Png&isCircular=false")

        if (ThumbnailRequest.status_code != 200 or IconRequest.status_code != 200):
            return None, None

        ThumbnailRequestJson = ThumbnailRequest.json()
        Thumbnails = ThumbnailRequestJson["data"][0]["thumbnails"]

        ThumbnailImageUrls = []
        
        for x in Thumbnails:
            ThumbnailImageUrls.append(x["imageUrl"])

        IconRequestJson = IconRequest.json()
        Icon = IconRequestJson["data"][0]["imageUrl"]

        return ThumbnailImageUrls, Icon
            

        # if (CanDownloadMetadata):
        #     obj = json.loads(dlAssetMetadata.content)
        #     open(Directory + "Metadata.json", "w", encoding='utf-8').write(json.dumps(obj, indent=4))

        # assetInfo = dlAssetMetadata.json()
        # assetName = assetInfo["Name"]
        # assetTypeId = assetInfo["AssetTypeId"]
        # creatorName = assetInfo["Creator"]["Name"]
        # AssetTypeName = AssetDownloader.assetTypeList[assetTypeId - 1]
        # assetDate = f"{AssetDownloader.fixBadStr(headers['Last-Modified'])[5:-4]}"

        # return [assetInfo, assetName, assetTypeId, creatorName, AssetTypeName, assetDate]

    def assetExt(assetTypeId):
        if assetTypeId == 1: fileExt = ".png"
        elif assetTypeId == 3: fileExt = ".mp3"
        elif assetTypeId == 4: fileExt = ".mesh"
        elif assetTypeId == 5: fileExt = ".lua"
        elif assetTypeId == 9: fileExt = ".rbxl"
        else: fileExt = ".rbxm"
        return fileExt

    def DownloadAsset(AssetID, VersionNumber):
        FileName = "DownloadedAsset"
        FileType = ".rbxm"

        print("Downloading " + AssetID + "...")
        Widget.ProgressBar.setMaximum(0)
        Widget.AssetInput.setEnabled(False)
        dlAsset = requests.get(f'{assetUrl}{AssetID}&version={VersionNumber}', headers = headersIn, stream=True)
        FileSize = dlAsset.headers["content-length"]
        BlockSize = 1024

        if (dlAsset.status_code != 200):
            QtWidgets.QMessageBox.critical(MainWidget(), "Error!", "Download failed! Status code " + str(dlAsset.status_code))

            return dlAsset.status_code

        MetaData = AssetDownloader.DownloadMetadata(AssetID, dlAsset.headers)

        if (MetaData != None):
            assetInfo = MetaData.json()
            assetName = assetInfo["Name"]
            assetTypeId = assetInfo["AssetTypeId"]
            creatorName = assetInfo["Creator"]["Name"]
            AssetTypeName = AssetDownloader.assetTypeList[assetTypeId - 1]
            assetDate = f"{dlAsset.headers['Last-Modified']}" # [5:-4]

            FileName = AssetDownloader.fixBadStr(assetName)
            FileType = AssetDownloader.assetExt(assetTypeId)

        if (VersionNumber != 0):
            FileName += f" ({VersionNumber})"

        os.mkdir(os.path.join(os.getcwd(), FileName))
        # Widget.ProgressBar.setMaximum(int(FileSize))

        with open(f'{FileName}/{FileName}{FileType}', 'wb') as file:
            for data in dlAsset.iter_content(BlockSize):
                #Widget.ProgressBar.setValue(len(data))
                file.write(data)

        if (AssetTypeName == "Place"):
            Thumbnails, Icon = AssetDownloader.DownloadThumbnails(AssetID, AssetDownloader.ThumbnailSize, AssetDownloader.IconSize)

            IconRequest = requests.get(Icon)

            if (IconRequest.status_code == 200):
                open(f'{FileName}/Icon.png', "wb").write(IconRequest.content)

            counter = 1
            for thumbnail in Thumbnails:
                image = requests.get(thumbnail)

                if (image.status_code == 200):
                    open(f'{FileName}/Thumbnail ({counter}).png', "wb").write(image.content)
                    counter += 1
        else:
            AssetIconURL = AssetDownloader.DownloadAssetIcon(AssetID, AssetDownloader.AssetSize)

            if (AssetIconURL != None):
                AssetIcon = requests.get(AssetIconURL)
                open(f'{FileName}/Icon.png', "wb").write(AssetIcon.content)


        # open(f'{FileName}/{FileName}{FileType}', "wb").write(dlAsset.content)

        if (CanDownloadMetadata and MetaData != None):
            obj = json.loads(MetaData.content)
            open(f'{FileName}/Metadata.json', "w", encoding='utf-8').write(json.dumps(obj, indent=4))

            # Write last modified date:
            Path = f'{FileName}/{FileName}{FileType}'
            temp_time = time.strptime(assetDate, "%a, %d %b %Y %H:%M:%S %Z")
            epoch_time = time.mktime(temp_time)

            os.utime(Path, (epoch_time, epoch_time))

            # if (AssetTypeName == "Place" and Thumbnails != None and Icon != None):
            #     IconRequest = requests.get(Icon)

            #     if (IconRequest.status_code == 200):
            #         open(f'{FileName}/Icon.png', "wb").write(IconRequest.content)

            #     counter = 1
            #     for thumbnail in Thumbnails:
            #         image = requests.get(thumbnail)

            #         if (image.status_code == 200):
            #             open(f'{FileName}/Thumbnail ({counter}).png', "wb").write(image.content)
            #             counter += 1
        
        Widget.ProgressBar.setMaximum(100)
        Widget.AssetInput.setEnabled(True)

    def DownloadAllAssets(versionNumber, WidgetMain):
        print(versionNumber)
        for x in range(int(versionNumber)):
            print(x + 1)
            AssetDownloader.DownloadAsset(WidgetMain.AssetInput.text(), x + 1)

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hashbrown")
        self.setWindowIcon(QtGui.QIcon('StudioIcon.png'))

        self.InitMainUI()
        self.MenubarInit()
        self.SettingsMenuInit()
        self.AboutMenuInit()

    def InitMainUI(self):
        self.AssetInput = QtWidgets.QLineEdit(self)
        self.AssetInput.setGeometry(4, 24, 128, 24)
        self.AssetInput.setAlignment(QtCore.Qt.AlignHCenter)
        self.AssetInput.setPlaceholderText("Insert Asset ID/Hash")

        self.VersionInput = QtWidgets.QSpinBox(self)
        self.VersionInput.setMaximum(2048)
        self.VersionInput.setGeometry(136, 24, 64, 24)

        self.DownloadAllVersions = QtWidgets.QCheckBox(self)
        self.DownloadAllVersions.setText("Download all versions")
        self.DownloadAllVersions.setGeometry(204, 24, 256, 24)

        self.DownloadAllVersions.clicked.connect(self.ToggleDownloadAllVersions)

        DownloadButton = QtWidgets.QPushButton("Download", self)
        DownloadButton.setGeometry(4, 48, 96, 32)

        DownloadButton.clicked.connect(self.InitializeDownload)
        
        self.ProgressBar = QtWidgets.QProgressBar(self)
        self.ProgressBar.setGeometry(4, 104, 256, 24)

        self.StatusLabel = QtWidgets.QLabel(self)
        self.StatusLabel.setText("Ready.")
        self.StatusLabel.setGeometry(4, 80, 128, 16)

    # def UpdateProgressBar(self, value):
    #     self.ProgressBar.setValue(value)

    def ToggleDownloadAllVersions(self):
        self.VersionInput.setEnabled(not self.DownloadAllVersions.isChecked())

    def InitializeDownload(self):
        # Widget.ProgressBar.setMaximum(0)

        # self.AssetInput.setEnabled(False)
        if (self.DownloadAllVersions.isChecked()):
            maxVerId = requests.get(f'https://assetdelivery.roblox.com/v1/assetid/{self.AssetInput.text()}', headers = headersIn)
            versionNumber = maxVerId.headers["roblox-assetversionnumber"]

            x = threading.Thread(target=AssetDownloader.DownloadAllAssets, args=(versionNumber, self))
            x.start()

            # self.thread = QtCore.QThread()
            # Downloader = AssetDownloader()
            # Downloader.moveToThread(self.thread)
            # self.thread.started.connect(lambda: Downloader.DownloadAllAssets(versionNumber, self))
            # self.thread.finished.connect(self.thread.quit)
            # self.thread.start(QtCore.QThread.LowestPriority)
            #Downloader.finished.connect(thread.quit)
            #thread.DownloadAllAssets(versionNumber)
            #thread.quit()
        else:
            x = threading.Thread(target=AssetDownloader.DownloadAsset, args=(self.AssetInput.text(), self.VersionInput.value()))
            x.start()
        # self.AssetInput.setEnabled(True)
        # print("Download complete")

    def ApplySettings(self):
        # ThumbnailSize = ThumbnailSizes[self.SettingsWidget.ThumbnailSizesDropdown.currentIndex()]
        AssetDownloader.ThumbnailSize = AssetDownloader.ThumbnailSizes[self.SettingsWidget.ThumbnailSizesDropdown.currentIndex()]
        AssetDownloader.IconSize = AssetDownloader.IconSizes[self.SettingsWidget.IconSizesDropdown.currentIndex()]
        AssetDownloader.AssetSize = AssetDownloader.AssetSizes[self.SettingsWidget.AssetSizesDropdown.currentIndex()]
        print(AssetDownloader.ThumbnailSize)

    def SettingsMenuInit(self):
        self.SettingsWidget = QtWidgets.QWidget()
        self.SettingsWidget.setWindowTitle("Settings")
        self.SettingsWidget.setWindowIcon(QtGui.QIcon('StudioIcon.png'))
        self.SettingsWidget.setFixedSize(640, 480)
        self.SettingsWidget.setStyleSheet(open("style/style.css").read())

        #Thumbnail resolution option
        ThumbnailSizeOptionText = QtWidgets.QLabel(self.SettingsWidget)
        ThumbnailSizeOptionText.setText("Thumbnail resolution:")
        ThumbnailSizeOptionText.setGeometry(4, 4, 128, 24)

        self.SettingsWidget.ThumbnailSizesDropdown = QtWidgets.QComboBox(self.SettingsWidget)
        self.SettingsWidget.ThumbnailSizesDropdown.setGeometry(132, 4, 128, 24)

        for x in AssetDownloader.ThumbnailSizes:
            self.SettingsWidget.ThumbnailSizesDropdown.addItem(x)

        #Icon resolution option
        IconSizeOptionText = QtWidgets.QLabel(self.SettingsWidget)
        IconSizeOptionText.setText("Icon resolution:")
        IconSizeOptionText.setGeometry(4, 32, 128, 24)

        self.SettingsWidget.IconSizesDropdown = QtWidgets.QComboBox(self.SettingsWidget)
        self.SettingsWidget.IconSizesDropdown.setGeometry(132, 32, 128, 24)

        for x in AssetDownloader.IconSizes:
            self.SettingsWidget.IconSizesDropdown.addItem(x)

        self.SettingsWidget.IconSizesDropdown.setCurrentIndex(4)

        #asset resolution option
        AssetSizeOptionText = QtWidgets.QLabel(self.SettingsWidget)
        AssetSizeOptionText.setText("Asset icon resolution:")
        AssetSizeOptionText.setGeometry(4, 60, 128, 24)

        self.SettingsWidget.AssetSizesDropdown = QtWidgets.QComboBox(self.SettingsWidget)
        self.SettingsWidget.AssetSizesDropdown.setGeometry(132, 60, 128, 24)

        for x in AssetDownloader.AssetSizes:
            self.SettingsWidget.AssetSizesDropdown.addItem(x)

        self.SettingsWidget.AssetSizesDropdown.setCurrentIndex(18)

        ApplyButton = QtWidgets.QPushButton(self.SettingsWidget)
        ApplyButton.setText("Apply")
        ApplyButton.setGeometry(540, 444, 96, 32)

        ApplyButton.clicked.connect(self.ApplySettings)

    def ShowSettingsMenu(self):
        self.SettingsWidget.show()

    def AboutMenuInit(self):
        self.AboutWidget = QtWidgets.QWidget()
        self.AboutWidget.setWindowTitle("About")
        self.AboutWidget.setFixedSize(256, 64)
        self.AboutWidget.setStyleSheet(open("style/style.css").read())

        AboutText = QtWidgets.QLabel("KeyboardCombination 2022", alignment=QtCore.Qt.AlignCenter)
        AboutText.setGeometry(0, 0, 256, 64)
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

    Widget.setStyleSheet(open("style/style.css").read())

    sys.exit(HashbrownApp.exec())