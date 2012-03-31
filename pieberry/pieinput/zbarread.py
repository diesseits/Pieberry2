import sys, os, os.path, datetime
from pieberry.pieconfig.globalvars import ZBAR
from pieberry.piescrape.googlebooks import *

if ZBAR:
    import zbar
# from threading import Thread

if __name__ == '__main__': 
    stalone = True
else: 
    stalone = False
    from pieberry.pieconfig.config import PIE_CONFIG

print 'run standalone', stalone

class PieZbarScanner:
    '''A class to access a barcode scanner through the webcam using
    the zbar library, grabbing an ISBN code.'''
    def __init__(self, *args, **kwargs):
        self.proc = zbar.Processor()
        self.loop = False

    def _init_webcam(self):
        self.proc.parse_config('enable')
        device = PIE_CONFIG.get('Internal', 'webcam_device')
        self.proc.init(device)
        self.proc.visible = True
        print 'web cam init done'
        return True
        
    def _do_scan(self):
        self.proc.process_one()
        for symbol in self.proc.results:
            # do something useful with results
            print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            # check if type is isbn
            if str(symbol.type).find("ISBN") > -1:
                return str(symbol.data)
            else:
                return None

    def DoScan(self):
        print 'DoScan'
        init_res = self._init_webcam()
        print 'webcam initialized'
        if init_res == False: yield False
        self.loop = True
        while self.loop:
            try:
                data = self._do_scan()
            except zbar.WindowClosed:
                print 'zbar.WindowClosed exception caught'
                return
            if data:
                print data
                yield data

    def EndScan(self):
        self.loop = False
        self.proc.visible = False

if __name__ == '__main__':
    zbs = PieZbarScanner()
    for i in zbs.DoScan(): 
        print i
    print 'done'

example_scanresult = 'decoded UPCE symbol "08242224"'
