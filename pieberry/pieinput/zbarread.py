import sys, os, os.path, datetime
from pieberry.pieconfig.globalvars import ZBAR
from pieberry.piescrape.googlebooks import *
from pieberry.ui.events import PieBarcodeEvent
from threading import Thread

if ZBAR:
    import zbar
# from threading import Thread

if __name__ == '__main__': 
    stalone = True
else: 
    stalone = False
    from pieberry.pieconfig.config import PIE_CONFIG

class PieZbarScanner(Thread):
    '''A class to access a barcode scanner through the webcam using
    the zbar library, grabbing an ISBN code.'''
    def __init__(self, notify_window, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.proc = zbar.Processor()
        # self.loop = False
        self.notify_window = notify_window

    def _init_webcam(self):
        self.proc.parse_config('enable')
        device = PIE_CONFIG.get('Internal', 'webcam_device')
        self.proc.init(device)
        self.proc.visible = True
        self.proc.set_data_handler(self.HandleData)
        print 'web cam init done'
        return True
        
    # def _do_scan(self):
    #     self.proc.process_one()
    #     for symbol in self.proc.results:
    #         # do something useful with results
    #         print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    #         # check if type is isbn
    #         if str(symbol.type).find("ISBN") > -1:
    #             return str(symbol.data)
    #         else:
    #             return None

    def run(self):
        print 'DoScan'
        init_res = self._init_webcam()
        print 'webcam initialized'
        self.proc.active = True
        try:
            self.proc.user_wait()
        except zbar.WindowClosed:
            self.EndScan()
            return

    def DoScan(self):
        print 'DoScan'
        init_res = self._init_webcam()
        print 'webcam initialized'
        if init_res == False: yield False
        self.loop = True
        self.proc.active = True
        try:
            # self.proc.user_wait()
            while self.loop:
                self.proc.scan_one()
        except zbar.WindowClosed:
            print 'zbar.WindowClosed caught'
            self.EndScan()
            return
        # while self.loop:
            
            # try:
            #     data = self._do_scan()
            # except zbar.WindowClosed:
            #     print 'zbar.WindowClosed exception caught'
            #     return
            # if data:
            #     print data
            #     yield data

    def EndScan(self):
        print 'terminating loop'
        self.loop = False
        # print 'making invisible'
        # self.proc.visible = False
        # print 'making inactive'
        # self.proc.active = False
        # # self.loop = False

    def HandleData(self, proc, image, closure):
        '''Handle the barcode data that has been found, emit an event'''
        print 'HandleData'
        for symbol in image:
            if not symbol.count:
                # do something useful with results
                print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
                if str(symbol.type).find("ISBN") > -1:
                    newevt = PieBarcodeEvent(
                        btype = symbol.type,
                        bcode = symbol.data)
                    print 'Posting event'
                    wx.PostEvent(self.notify_window, newevt)

if __name__ == '__main__':
    zbs = PieZbarScanner()
    for i in zbs.DoScan(): 
        print i
    print 'done'

example_scanresult = 'decoded UPCE symbol "08242224"'
