

class PieFileIndexer:
    '''A class which indexes the user's files, looks for disappeared
    files, looks for where they may have reappeared, and looks for new
    files and puts them into the database.'''
    def __init__(self):
        pass

    def DoScanForMissing(self):
        pass

    def DoScanForNew(self):
        pass

    def MatchMissingFile(self, obj):
        # propose the following tests:
        # 1) File with the same name & size in different location
        # 2) File with different name with same size & location
        # 3) File with different name & location but same size and ???
        pass
