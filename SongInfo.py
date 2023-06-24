class SongInfo:
    songTitle = ""
    performer = ""
    startTime = 0
    endTime = 0
    track = 0

    def __init__(self, title, performer, startTime, endTime, track):
        self.songTitle = title
        self.performer = performer
        if isinstance(startTime, (str)):
            self.startTime = timeTransfer(startTime)
        elif isinstance(startTime, (float, int)):
            self.startTime = startTime
        if isinstance(endTime, (str)):
            self.endTime = timeTransfer(endTime)
        elif isinstance(endTime, (float, int)):
            self.endTime = endTime
        if track > 0:
            self.track = track

    def print(self):
        print("-" * 30, "\n\tTitle : %s\n" % self.songTitle, "\tPerformer : %s\n" % self.performer,
              "\tTrack : %d\n" % self.track, "\tstratTime : %d\n" % self.startTime, "\tendTime : %d\n" % self.endTime,
              "duration : ")
        returnTime((self.endTime - self.startTime) / 1000)
        print('\n')

    def getTitle(self):
        return self.songTitle

    def getDuration(self):
        return "%d:%d" % (
            (self.endTime - self.startTime) // 60000, (self.endTime - self.startTime) / 1000 % 60)

    def text(self):
        return (
                "-" * 30 + "\nTrack : %d\n" % self.track + "\tTitle : %s\n" % self.songTitle + "\tPerformer : %s\n" % self.performer + "\tstratTime : %d\n" % self.startTime + "\tendTime : %d\n" % self.endTime +
                "\tduration : %d:%d\n" % (
                    (self.endTime - self.startTime) // 60000, (self.endTime - self.startTime) / 1000 % 60))


def timeTransfer(string):  # str format： "xx:xx:xx" , Process and return time number (m second)
    if checkTimeFormat(string):
        slices = str.split(string, ":")

        return int((int(slices[0]) * 60000 + int(slices[1]) * 1000 + int(slices[2]) * 800 / 75))
    return 0


def checkTimeFormat(string):
    slices = str.split(string, ":")
    if len(slices) == 3:
        for one in slices:
            if str.isdecimal(one) is not True:
                return False
    else:
        return False
    return True
    # print(slices)


def calc(a, b, c):
    tmp = a * 60 + b + c * 60 / 75 / 75
    returnTime(tmp)


def returnTime(num):
    # h=num%/60/60
    m = int(num // 60)
    s = num % 60
    print(m, s)


if __name__ == '__main__':
    print(checkTimeFormat("12:12:01"))
    (calc(4, 21, 61))
