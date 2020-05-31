class HistoryLogger(object):
    """ 
    Outputs all informations of the script editor in an external file
    Useful to debug a script that crashes, 
    as it'll write the contents of the script editor in an external file
    To use it, create an instance of the class and call toggleHistory()
     """

    def __init__(self, filePath):
        self.filePath = filePath
    def logOn(self):
        # turn history on
        mc.scriptEditorInfo(historyFilename=self.filePath, writeHistory = True, clearHistoryFile = True)
        print '===================================='
        print ' History ON : outputs in : ' + self.filePath
        print '===================================='
    def logOff(self):
        mc.scriptEditorInfo(writeHistory = False)
        print '===================================='
        print ' History OFF : outputs in : ' + self.filePath
        print '===================================='

    def toggleHistory(self):
        currentStatus = mc.scriptEditorInfo(q=True, writeHistory=True)
        self.logOff() if currentStatus else self.logOn()
        
    def getInfos(self):
        currentStatus = mc.scriptEditorInfo(q=True, writeHistory=True)
        if currentStatus:
            print 'Logging is currently ON '
            print 'Outputing in file : ' + self.filePath
        else:
            print 'Logging is currently OFF '
hist = HistoryLogger('/tmp/history.txt')
hist.toggleHistory()