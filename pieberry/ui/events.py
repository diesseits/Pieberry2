import wx
import wx.lib.newevent

PieListSelectionEvent, EVT_PIE_LIST_SELECTION_EVENT = wx.lib.newevent.NewEvent()
# use 'ref' for objectstore reference, 'pieobject' for selected object
PieSearchEvent, EVT_PIE_SEARCH_EVENT = wx.lib.newevent.NewEvent()
# use 'searchtext' to store search string
PieWebScrapeEvent, EVT_PIE_SCRAPE_EVENT = wx.lib.newevent.NewEvent()
# attributes: url, catstring, catbehaviour, author, authoriscorporate
PieDownloadEvent, EVT_PIE_DOWNLOAD = wx.lib.newevent.NewEvent()
# attributes: ostore - the objects to be downloaded
#             pane - the pane it originates from
PieDownloadNotifyEvent, EVT_PIE_DOWNLOAD_NOTIFY = wx.lib.newevent.NewEvent()
# attributes: msgtype (start, success, fail, warn), obj, notify_window
