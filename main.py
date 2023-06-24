# 将整个专辑的单个音频文件CDImage.wav按照cue文件的说明
# 1.切分成多个文件
# 2.将各音频文件写入标签信息


# 目前的问题是要解决多线程问题

import atexit
import glob
import os
import re
from threading import Thread

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTreeWidget, QTreeWidgetItem
from pydub import AudioSegment

from SongInfo import *

# global currentPath
currentPath = "D:"
fileFolderPath = "D:"
destinationPath = "D:"


# class MySignals(QObject):
#     logSingal = pyqtSignal(str)


class Worker(QObject):
    logSig = pyqtSignal(str)
    startSig = pyqtSignal()
    endSig = pyqtSignal()
    addAlbumToTreeSig = pyqtSignal(str)
    # addSongToTreeSig=pyqtSignal(str)
    addSongDetailToTreeSig = pyqtSignal(SongInfo)
    counterSig = pyqtSignal(int)
    cnt = 0

    def __init__(self):
        super(Worker, self).__init__()

    def working(self):
        print("worker_thread")
        self.startSig.emit()
        self.startButtonEvent()
        self.endSig.emit()

    def showSongInfo(self, songInfo):
        pass
        # self.addSongToTreeSig.emit(songInfo.songTitle)
        # self.logSig.emit(
        #     "-" * 30 + "\nTrack : %d\n" % songInfo.track + "\tTitle : %s\n" % songInfo.songTitle + "\tPerformer : %s\n" % songInfo.performer + "\tstratTime : %d\n" % songInfo.startTime + "\tendTime : %d\n" % songInfo.endTime +
        #     "\tduration : %d:%d\n" % (
        #         (songInfo.endTime - songInfo.startTime) // 60000, (songInfo.endTime - songInfo.startTime) / 1000 % 60))

    # def consoleLogAppend(self, str):
    #     self.ui.consoleLog.append(str)
    #     self.ui.consoleLog.ensureCursorVisible()
    #
    # def consoleLogAppendUtil(self, str):
    #     self.logSignal.logSingal.emit(str)

    def songSplice(self, cuePath):

        # SongInfo("","","","")
        info = cueProcess(cuePath)
        print(info)
        for fileName in info['files']:
            songPath = os.path.split(cuePath)[0] + '\\' + fileName
            # print(songPath)
            ext = str.split(os.path.splitext(fileName)[1])[-1]
            try:
                self.addAlbumToTreeSig.emit(info['album'])
                sound = AudioSegment.from_file(songPath)
                songCnt = 1
                for song in info[fileName]:
                    slice = sound[song.startTime:song.endTime]
                    # title=song.getTitle()
                    # title='out/'+title
                    # print(song.songTitle)
                    # consoleThread = Thread(self.showSongInfo(song), args=song,daemon=True)
                    # consoleThread.start()
                    self.logSig.emit(song.text())
                    # self.addSongToTreeSig.emit(str(cnt)+'. '+song.songTitle)
                    self.addSongDetailToTreeSig.emit(song)
                    # consoleThread.join()
                    newFolder = destinationPath + "/" + info['album'] + "/"
                    newSongPath = newFolder + song.performer + ' - ' + song.songTitle + '.wav'
                    # print(newFolder)
                    if not os.path.exists(newFolder):
                        os.makedirs(newFolder)
                    songCnt += 1
                    self.cnt += 1
                    self.counterSig.emit(self.cnt)

                    slice.export(newSongPath, format='wav')
                    # slice.export(newSongPath, format='wav')
                    # songFile=WAVE(newSongPath)
                    # songFile.tags.update_to_v23()
                    # songFile.pprint()
            except FileNotFoundError:
                print("File is not exits")

    def startButtonEvent(self):
        path = glob.escape(fileFolderPath) + "/**/*.cue"
        cuePaths = glob.glob(path, recursive=True)
        self.cnt = 0

        for cuePath in cuePaths:
            self.songSplice(cuePath)


class ClearWorker(QObject):
    sig = pyqtSignal()

    def clearWorking(self):
        self.sig.emit()


class Spleeter(QMainWindow):
    # Path -> file & tool
    # c = "D:"
    # fileFolderPath = "D:"
    # destinationPath = "D:"
    # logSignal = MySignals()
    log = None
    threads = []
    worker = None
    clearWorker = None
    lastAlbum = None

    # lastSong=None

    def __init__(self):
        # 将save函数 作为程序终止前 的触发任务
        super().__init__()
        atexit.register(self.save)
        global currentPath
        currentPath = os.getcwd()
        self.ui = uic.loadUi(currentPath + "/CDImageSplice-beta.ui")
        # log = self.ui.consoleLog
        self.fileLoad()
        self.worker = Worker()
        self.clearWorker = ClearWorker()
        for i in range(3):
            self.threads.append(QThread())
        self.initialize()
        # self.logSignal.logSingal.connect(self.consoleLogAppend)
        self.threads[0].start()
        self.threads[1].start()

    def initialize(self):
        self.ui.filePathButton.clicked.connect(self.changeFileFolder)
        self.ui.destPathButton.clicked.connect(self.changeDestFolder)

        self.worker.logSig.connect(self.consoleLogAppend)
        self.worker.startSig.connect(self.makeSomeWidgetsDisable)
        self.worker.endSig.connect(self.makeSomeWidgetsAble)

        self.clearWorker.sig.connect(self.clearLog)

        self.worker.moveToThread(self.threads[0])
        self.clearWorker.moveToThread(self.threads[1])
        # self.threads[0].connect(self.worker.startButtonEvent)
        # startWorder=Worker()

        self.ui.startButton.clicked.connect(self.worker.working)
        self.ui.clearLogButton.clicked.connect(self.clearWorker.clearWorking)

        # treeWidget
        self.ui.tree.setColumnCount(2)
        self.worker.addAlbumToTreeSig.connect(self.addAlbumToTree)
        # self.worker.addSongToTreeSig.connect(self.addSongToTree)
        self.worker.addSongDetailToTreeSig.connect(self.addSongDetailToTree)
        # 《测试用例
        # self.addAlbumToTree("testAlbum")
        # self.addSongToTree("testSong")
        # self.addSongToTree("testSong")
        # self.addAlbumToTree("testAlbum")
        # self.addSongToTree("testSong")
        # 测试用例》
        #
        #
        self.worker.counterSig.connect(self.showCounter)

        self.refreshFilePath()
        self.refreshDestPath()

    def refreshFilePath(self):
        self.ui.filePath.setText(fileFolderPath)

    def refreshDestPath(self):
        self.ui.destPath.setText(destinationPath)

    def folderSelect(self, originStr=""):
        tmp = QFileDialog.getExistingDirectory(self.ui, "请选择文件夹路径", options=QFileDialog.DontUseNativeDialog)
        if tmp != "":
            return tmp
        else:
            return originStr

    def changeFileFolder(self):
        global fileFolderPath
        fileFolderPath = self.folderSelect(originStr=fileFolderPath)
        self.refreshFilePath()

    def changeDestFolder(self):
        global destinationPath
        destinationPath = self.folderSelect(destinationPath)
        self.refreshDestPath()

    def fileLoad(self):
        global fileFolderPath, destinationPath
        # global destinationPath
        config = open(currentPath + '/properties.ini', 'r+', encoding='utf-8')
        string = config.read()
        #  print(string)
        paths = re.findall("fileFolderPath=(.*)", string)
        if paths is not None:
            fileFolderPath = paths[0]
        paths = re.findall("destinationPath=(.*)", string)
        # print(paths)
        if paths is not None:
            destinationPath = paths[0]
        # isChecked = re.findall("deleteCheckBox=(.*)", string)
        # if isChecked is not None:
        #     if isChecked[0] == "False":
        #         self.ui.deleteCheckBox.setCheckState(Qt.Unchecked)
        #     else:
        #         self.ui.deleteCheckBox.setCheckState(Qt.Checked)

    def save(self):
        config = open(currentPath + '/properties.ini', 'w', encoding='utf-8')
        config.write("fileFolderPath=" + fileFolderPath + os.linesep)
        config.write("destinationPath=" + destinationPath + os.linesep)
        # config.write("toolPath=" + self.toolPath + os.linesep)
        # config.write("deleteCheckBox=" + str(self.ui.deleteCheckBox.isChecked()) + os.linesep)
        config.close()
        # print("saved")

    def showSongInfo(self, songInfo):
        self.ui.consoleLogAppendUtil(
            "-" * 30 + "\nTrack : %d\n" % songInfo.track + "\tTitle : %s\n" % songInfo.songTitle + "\tPerformer : %s\n" % songInfo.performer + "\tstratTime : %d\n" % songInfo.startTime + "\tendTime : %d\n" % songInfo.endTime +
            "\tduration : %d:%d\n" % (
                (songInfo.endTime - songInfo.startTime) // 60000, (songInfo.endTime - songInfo.startTime) / 1000 % 60))

    def consoleLogAppend(self, str):
        self.ui.consoleLog.append(str)
        self.ui.consoleLog.ensureCursorVisible()

    # def consoleLogAppendUtil(self, str):
    #     self.logSignal.logSingal.emit(str)

    def songSplice(self, cuePath):

        # SongInfo("","","","")
        info = cueProcess(cuePath)
        for fileName in info['files']:
            songPath = os.path.split(cuePath)[0] + '\\' + fileName
            # print(songPath)
            ext = str.split(os.path.splitext(fileName)[1])[-1]
            try:
                sound = AudioSegment.from_file(songPath)
                for song in info[fileName]:
                    slice = sound[song.startTime:song.endTime]
                    # title=song.getTitle()
                    # title='out/'+title
                    # print(song.songTitle)
                    # consoleThread = Thread(self.showSongInfo(song), args=song,daemon=True)
                    # consoleThread.start()
                    # self.consoleLogAppendUtil(song.text())
                    # consoleThread.join()
                    newFolder = destinationPath + "/" + info['album'] + "/"
                    newSongPath = newFolder + song.performer + ' - ' + song.songTitle + '.wav'
                    # print(newFolder)
                    if not os.path.exists(newFolder):
                        os.makedirs(newFolder)
                    slice.export(newSongPath, format='wav')
                    # slice.export(newSongPath, format='wav')
                    # songFile=WAVE(newSongPath)
                    # songFile.tags.update_to_v23()
                    # songFile.pprint()
            except FileNotFoundError:
                print("File is not exits")

    def startButtonEventThread(self):

        thread = Thread(self.startButtonEvent())
        thread.start()

    def startButtonEvent(self):
        path = glob.escape(fileFolderPath) + "/**/*.cue"
        cuePaths = glob.glob(path, recursive=True)
        # print("'start':", path)
        # print(cuePaths)
        # self.ui.consoleLog.append(cuePaths.__str__())
        for cuePath in cuePaths:
            self.songSplice(cuePath)

    def makeSomeWidgetsDisable(self):
        self.ui.filePathButton.setEnabled(False)
        self.ui.destPathButton.setEnabled(False)
        self.ui.startButton.setEnabled(False)

    def makeSomeWidgetsAble(self):
        self.ui.filePathButton.setEnabled(True)
        self.ui.destPathButton.setEnabled(True)
        self.ui.startButton.setEnabled(True)

    def clearLog(self):
        self.ui.consoleLog.clear()
        print("ClearButton Clicked!")

    # treeWidget
    def addAlbumToTree(self, info):
        album = QTreeWidgetItem(self.ui.tree)
        album.setText(0, info)
        self.lastAlbum = album
        # QTreeWidget().insertTopLevelItem()

    def addSongToTree(self, info):
        if self.lastAlbum is not None:
            song = QTreeWidgetItem(self.lastAlbum)
            song.setText(0, info)
            # self.lastSong=song

    def addSongDetailToTree(self, songInfo):
        if self.lastAlbum is not None:
            song = QTreeWidgetItem(self.lastAlbum)
            song.setText(0, songInfo.songTitle)
            artist = QTreeWidgetItem(song)
            start = QTreeWidgetItem(song)
            end = QTreeWidgetItem(song)
            duration = QTreeWidgetItem(song)
            artist.setText(0, "Artist:")
            start.setText(0, "StartTime:")
            end.setText(0, "EndTime:")
            duration.setText(0, "Duration:")
            artist.setText(1, songInfo.performer)
            start.setText(1, str(songInfo.startTime))
            end.setText(1, str(songInfo.endTime))
            duration.setText(1, songInfo.getDuration())

    def showCounter(self, number):
        self.ui.counter.display(number)


def cueProcess(cuePath):
    # global sound
    cueFile = open(cuePath, "r", encoding='utf-8-sig')
    with cueFile as file:
        string = file.read()
        print(string)
        # if string.startswith(u'/ufeff'):
        #     string = string.encode('utf8')[3:].decode('utf8')
    currentPath = os.path.split(cuePath)
    m = {}  # {"PERFORMER":"","ALBUM":"",subMap{}}
    songMap = {}  # {"TITLE":"TRACK 01 TIME",......}
    fileNames = re.findall("FILE \"(.*)\" ", string)
    fileBranches = str.split(string, "FILE")
    # print("fileBranches:\n", fileBranches)
    m["album"] = re.search("TITLE \"(.*)\"", string).group(1)
    date = re.search("DATE (.*)", string)
    if date is not None:
        m["date"] = date.group(1)
    m["files"] = fileNames
    songs = []

    globalPerformer = re.search("PERFORMER \"(.*)\"", fileBranches[0]).group(1)
    cnt = 1
    for i in range(1, len(fileBranches)):
        # print(fileBranches[i])
        tracks = str.split(fileBranches[i], "TRACK ")
        # print("tracks:\n", tracks)
        m[fileNames[i - 1]] = []
        for j in range(1, len(tracks) - 1):
            # print(tracks[j])
            try:
                title = re.search("TITLE \"(.*)\"\n", tracks[j]).group(1)
                # print(title)
                performer = re.search("PERFORMER \"(.*)\"", tracks[j])
                if performer is not None:
                    performer = performer.group(1)
                else:
                    performer = globalPerformer
                # print(performer)
                startTime = re.search("INDEX 01 (.*)", tracks[j]).group(1)
                endTime = re.search("INDEX 00 (.*)", tracks[j + 1])
                if endTime is None or timeTransfer(endTime.group(1)) <= timeTransfer(startTime):
                    endTime = re.search("INDEX 01 (.*)", tracks[j + 1])
                    if endTime is not None:
                        endTime = endTime.group(1)
                else:
                    endTime = endTime.group(1)
                m[fileNames[i - 1]].append(
                    SongInfo(title=title, performer=performer, startTime=startTime, endTime=endTime, track=cnt))
                cnt += 1
            except Exception:
                print("Something got wrong")

        # print(tracks)
        # print(m)
        # print(tracks[-1])
        title = re.search("TITLE \"(.*)\"", tracks[len(tracks) - 1]).group(1)
        performer = re.search("PERFORMER \"(.*)\"", tracks[-1])
        if performer is not None:
            performer = performer.group(1)
        else:
            performer = globalPerformer
        startTime = re.search("INDEX 01 (.*)", tracks[-1]).group(1)
        try:
            sound = AudioSegment.from_file(os.path.split(cuePath)[0] + '\\' + m['files'][i - 1])
            endTime = len(sound)
        except FileNotFoundError:
            print("File is not exits")
            continue

        m[fileNames[i - 1]].append(SongInfo(title, performer, startTime, endTime, cnt))

        # string=strings[i]
        # m["PERFORMER"] = re.findall("PERFORMER \"(.*)\"", string)[0]
        # titles = re.findall("TITLE \"(.*)\"", string)
        # m["ALBUM"] = titles[0]
        # startTimes=re.findall("INDEX 01 (.*)",string)
        # m["FILE"] = re.findall("FILE \"(.*)\"", string)[0]
        # endTimes=re.findall("INDEX 00 (.*)",string)
        # #endTimes.append()
        # m["TITLES"]=titles
        # m["startTIMES"]=startTimes
        # m["endTIMES"]=endTimes
    return m
    #     subMap[titles[i]]=times[i-1]
    # subMap[t]


# return tree


if __name__ == '__main__':
    app = QApplication([])
    spleeter = Spleeter()
    spleeter.ui.show()
    app.exec_()
