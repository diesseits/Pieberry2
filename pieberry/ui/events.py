import wx
import wx.lib.newevent

PieListSelectionEvent, EVT_PIE_LIST_SELECTION_EVENT = wx.lib.newevent.NewEvent()
# use 'ref' for objectstore reference, 'pieobject' for selected object
PieSearchEvent, EVT_PIE_SEARCH_EVENT = wx.lib.newevent.NewEvent()
# use 'searchtext' to store search string
PieWebScrapeEvent, EVT_PIE_SCRAPE_EVENT = wx.lib.newevent.NewEvent()
# attributes: url, catstring, catbehaviour, author, authoriscorporate
PieUrlLoadedEvent, EVT_PIE_URL_LOADED = wx.lib.newevent.NewEvent()
PieUrlSnarfedEvent, EVT_PIE_URLS_SNARFED = wx.lib.newevent.NewEvent()
