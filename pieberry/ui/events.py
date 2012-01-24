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
PiePrefetchStartEvent, EVT_PIE_PREFETCH_START = wx.lib.newevent.NewEvent()
# attributes: url
PiePrefetchDoneEvent, EVT_PIE_PREFETCH_DONE = wx.lib.newevent.NewEvent()
# attributes: tag - the prefetched tag.
PieCommitStagedEvent, EVT_PIE_COMMIT_STAGED = wx.lib.newevent.NewEvent()
# attributes: ostore - the objects to be committed
#             pane - the originating pane
AtomDelFileEvent, EVT_ATOM_DEL_FILE = wx.lib.newevent.NewEvent()
# attributes: object - the object in question
#             rowid - the row it occupies in the atomWindow
AtomFileFileEvent, EVT_ATOM_FILE_FILE = wx.lib.newevent.NewEvent()
# attributes: object - the object in question
#             rowid - the row it occupies in the atomWindow
AtomOpenFileEvent, EVT_ATOM_OPEN_FILE = wx.lib.newevent.NewEvent()
# attributes: object - the object in question
#             rowid - the row it occupies in the atomWindow

