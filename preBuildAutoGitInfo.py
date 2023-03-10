from collections.abc import Iterable 
import datetime
import os


class Git:
    def __init__(self):
        pass

    def getUserName(self) -> str:
        return self._cmd(command="whoami")
    
    def getVersion(self) -> str:
        return self._cmd(command="git --version")
    
    def getBaseName(self) -> str:
        name = self._cmd("git rev-parse --show-toplevel")
        return name.split('/')[-1]
    
    def getNumberOfCommits(self) -> int:
        number = self._cmd("git rev-list --count HEAD")
        return int(number)
    
    def getBranch(self) -> str:
        return self._cmd('git name-rev --name-only --no-undefined HEAD')

    def getTag(self) -> list[int]:
        intTag = []
        commit = self.getCommitHash()
        tag = self._cmd(f"git tag --points-at {commit} ")
        if len(tag) == 0:
            intTag = [255, 255, 255]
        else:
            tag = tag.split(".")
            for i in tag:
                intTag.append(int(i))
        return intTag
    
    def getTagMajor(self) -> int:
        return self.getTag()[0]
    
    def getTagMinor(self) -> int:
        return self.getTag()[1]
    
    def getTagBuild(self) -> int:
        return self.getTag()[2]

    def getCommitHash(self, short: bool=False) -> str:
        if not short:
            return self._cmd(command="git rev-parse HEAD")
        else:
            return self._cmd(command="git rev-parse --short HEAD")

    def _cmd(self, command: str) -> str:
        return os.popen(command).read().strip()


class C_Header:
    FILE_BUFFER = ""
    DEFINE_HEADER = "AUTOREVISION_H"
    FILE_NAME = "autoGitInfo.h"
    DEFINE_PAD = 40

    def __init__(self) -> None:
        self._addHeader()

    def resetFile(self) -> None:
        self.FILE_BUFFER = ""

    def printFile(self) -> None:
        self._addFooter()
        print(self.FILE_BUFFER)

    def saveFile(self, filePath: str=".") -> None:
        temp = self.FILE_BUFFER.replace('\n',"")
        with open(f"{filePath}/{self.FILE_NAME}", 'w') as f:
            f.write(temp)

    def printAlignedDefine(self, name: str, value: str | int, comment: str=None, formatHex: bool=False) -> None:
        if comment != None:
            self._addCarriageReturn()
            self.FILE_BUFFER += "/*" + '  ' + comment + '  ' + "*/"
            self._addCarriageReturn()

        self.FILE_BUFFER += '#define ' + name + ' '

        for i in range(len(name), self.DEFINE_PAD):
            self.FILE_BUFFER += ' '

        if isinstance(value, str):
            self.FILE_BUFFER += '"' + value + '"'
        else:
            if isinstance(value, Iterable):
                index = 0
                for i in value:
                    if formatHex == True:
                        self.FILE_BUFFER += self._intToHex(i)
                    else:
                        self.FILE_BUFFER += str(i)
                    if index != (len(value) - 1):
                        self.FILE_BUFFER += ","
                    index += 1
            else:
                if formatHex == True:
                    self.FILE_BUFFER +=  self._intToHex(value)
                else:
                    self.FILE_BUFFER +=  str(value)
        self._addCarriageReturn()

    def _addCarriageReturn(self, number: int=1) -> None:
        for i in range(0, number):
            self.FILE_BUFFER += "\r\n"

    def _addHeader(self) -> None:
        self.FILE_BUFFER += "#ifndef " + self.DEFINE_HEADER
        self._addCarriageReturn()
        self.FILE_BUFFER += "#define " + self.DEFINE_HEADER
        self._addCarriageReturn(2)

    def _addFooter(self) -> None:
        if not "#endif" in self.FILE_BUFFER:
            self._addCarriageReturn(2)
            self.FILE_BUFFER += '#endif /*' + self.DEFINE_HEADER + '*/'
            self._addCarriageReturn()

    def _intToHex(self, inputVal: int) -> str:
        temp = hex(inputVal)[2:]
        if len(temp) == 1:
            temp = '0' + temp
        elif len(temp) != 2:
            temp = 'ff'
        return f"0x{temp.upper()}"


def getTime(isoFormat: bool=False) -> str:
    currentTime = datetime.datetime.now()
    if isoFormat:
        return currentTime.isoformat()
    else:
        return f"{currentTime.day:02d}.{currentTime.month:02d}.{currentTime.year}, {currentTime.hour:02d}:{currentTime.minute:02d}:{currentTime.second:02d}"


if __name__ == "__main__":
    gitClient = Git()
    c_cpp_header = C_Header()
    c_cpp_header.printAlignedDefine('VCS_TYPE', 'GIT', 'The version control software name')
    c_cpp_header.printAlignedDefine('VCS_TYPE_VERSION', gitClient.getVersion(), 'The version control software version')
    c_cpp_header.printAlignedDefine('VCS_BASENAME', gitClient.getBaseName() , 'Current project directory name')
    c_cpp_header.printAlignedDefine('VCS_NUM', gitClient.getNumberOfCommits(), 'Number of commits')
    c_cpp_header.printAlignedDefine('VCS_ISO_8601_DATE', getTime(isoFormat=True), 'ISO formated generation date')
    c_cpp_header.printAlignedDefine('VCS_LOCALE_DATE', getTime(isoFormat=False), 'Locale version of generation date')
    c_cpp_header.printAlignedDefine('VCS_BRANCH', gitClient.getBranch(), 'Current VCS branch')
    c_cpp_header.printAlignedDefine('VCS_SW_VERSION', gitClient.getTag(), 'Software version', formatHex=True)
    c_cpp_header.printAlignedDefine('VCS_SW_VERSION_MAJOR', gitClient.getTagMajor(), 'Software version major', formatHex=True)
    c_cpp_header.printAlignedDefine('VCS_SW_VERSION_MINOR', gitClient.getTagMinor(), 'Software version minor', formatHex=True)
    c_cpp_header.printAlignedDefine('VCS_SW_VERSION_BUILD', gitClient.getTagBuild(), 'Software version build', formatHex=True)
    # c_cpp_header.printAlignedDefine('VCS_TICK', tick, 'Amount of commit between the TAG and HEAD');
    # c_cpp_header.printAlignedDefine('VCS_WC_MODIFIED', modified, '1 if local repository changes, 0 otherwise (if not equal 0, VCS_SW_VERSION is 255,255,255)');
    c_cpp_header.printAlignedDefine('VCS_FULL_HASH', gitClient.getCommitHash(), 'The full git hash')
    c_cpp_header.printAlignedDefine('VCS_SHORT_HASH', gitClient.getCommitHash(short=True), 'The short git hash')
    c_cpp_header.printAlignedDefine('VCS_SYS_USERNAME', gitClient.getUserName(), 'Username of script the executor');

    c_cpp_header.printFile()
    c_cpp_header.saveFile()
