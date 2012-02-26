#GPLv3 Raif Sarcich 2011

from threading import Thread
from scraper import PieScraper

# Not using at the moment
class PieScraperThread(Thread, PieScraper):

    def __init__(self, notify_window, *args, **kwargs):
        self._notify_window = notify_window
        Thread.__init__(self)
        Scraper.__init__(self, *args, **kwargs)
        print 'ScraperThread initiated'

    def run(self):
        self._want_abort = 0

    def abort(self):
        self._want_abort = 1




