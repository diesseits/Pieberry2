#GPLv3 Raif Sarcich 2011

from threading import Thread
from scraper import Scraper

class ScraperThread(Thread, Scraper):

    def __init__(self, notify_window, url):
        Thread.__init__(self)
        Scraper.__init__(self)
        print 'ScraperThread initiated'

    def run(self):
        self._want_abort = 0

    def abort(self):
        self._want_abort = 1





