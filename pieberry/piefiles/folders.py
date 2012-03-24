import os, os.path, sys, wx, traceback, datetime, time, re
# from threading import Thread
# executive decision - this isn't going to be threaded

class PieFolderIndexer:
    '''A class which indexes the user's folders (that is to say - only
    folders, not the contents, which is done by a different, threaded,
    indexer'''
    def __init__(self, notify_window):
        self.nwin = notify_window

    def start(self):
        pass

    def DoScanForMissing(self, rootdir):
        pass

    def DoScanForNew(self, rootdir):
        pass
