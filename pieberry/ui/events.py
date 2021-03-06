import wx
import wx.lib.newevent

PieGenReportEvent, EVT_PIE_GEN_REPORT = wx.lib.newevent.NewEvent()
# attributes - ostore - all potential objects for the report
#            - subject - report subject
PieTagClickedEvent, EVT_PIE_TAG_CLICKED = wx.lib.newevent.NewEvent()
# attributes - tag - the tag clicked
PieTagRemovedEvent, EVT_PIE_TAG_REMOVED = wx.lib.newevent.NewEvent()
# attributes - tag - the tag removed
PieTagAddedEvent, EVT_PIE_TAG_ADDED = wx.lib.newevent.NewEvent()
# attributes - tag - the tag added
PieFileDroppedEvt, EVT_PIE_FILE_DROPPED = wx.lib.newevent.NewEvent()
# attributes - panel - originating panel
#              path - folder path shown in originating panel
#              filenames - list of filenames dropped
PieCrumbClickedEvent, EVT_PIE_CRUMB_CLICKED = wx.lib.newevent.NewEvent()
# attributes - fobj - the folder object
PieFolderClickedEvent, EVT_PIE_FOLDER_CLICKED = wx.lib.newevent.NewEvent()
# attributes - fobj - the folder object
#              notify_window - the window to address consequent calls
PieBarcodeEvent, EVT_PIE_BARCODE = wx.lib.newevent.NewEvent()
# attributes - btype - the barcode type
#            - bcode - the barcode data
PieUpdateAtomChoicesEvent, EVT_PIE_UPDATE_ATOM_CHOICES = wx.lib.newevent.NewEvent()
# attributes - dests - list of filesystem destinations
PieGoogleSearchEvent, EVT_PIE_GOOGLE_SEARCH = wx.lib.newevent.NewEvent()
# attributes - ostore - object store
PieLocationChangedEvent, EVT_PIE_LOCATION_CHANGED = wx.lib.newevent.NewEvent()
# No attributes
PieFileIndexFinishedEvent, EVT_PIE_FILE_INDEX_FINISHED = wx.lib.newevent.NewEvent()
# No attributesnotifyfobj
PieFileIndexEvent, EVT_PIE_FILE_INDEX = wx.lib.newevent.NewEvent()
# attributes: count (total no objects being indexed)
#             track (where we're up to in the above)
#             message (activity being conducted)
PieNotesPaneUpdateEvent, EVT_PIE_NOTES_PANE_UPDATE = wx.lib.newevent.NewEvent()
PieContextPanelFieldEvent, EVT_PIE_CONTEXT_PANEL_FIELD = wx.lib.newevent.NewEvent()
# attributes:  objattr  - the object attribute to modify
#              objattrval - the value to assign to the above
PieContextPanelUpdateEvent, EVT_PIE_CONTEXT_PANEL_UPDATE = wx.lib.newevent.NewEvent()
# attributes:  favourite (boolean)
PieGeneralUpdateEvent, EVT_PIE_GENERAL_UPDATE = wx.lib.newevent.NewEvent()
# all purpose update ui with new obj data event
# attributes:  obj - the object
#              notify_window - a listpanel to update
PieListSelectionEvent, EVT_PIE_LIST_SELECTION_EVENT = wx.lib.newevent.NewEvent()
# use 'ref' for objectstore reference, 'pieobject' for selected object
PieSearchEvent, EVT_PIE_SEARCH_EVENT = wx.lib.newevent.NewEvent()
# attributes: searchtext - to store search string
#             origin - 'origin' (storage virtual location) of files
#             fields - code for various search field combinations
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
#             auth - the default author from db
#             iscorp - whether default author is corporate
PieCommitStagedEvent, EVT_PIE_COMMIT_STAGED = wx.lib.newevent.NewEvent()
# attributes: ostore - the objects to be committed
#             pane - the originating pane
AtomDelFileEvent, EVT_ATOM_DEL_FILE = wx.lib.newevent.NewEvent()
# attributes: obj - the object in question
#             rowid - the row it occupies in the atomWindow
AtomFileFileEvent, EVT_ATOM_FILE_FILE = wx.lib.newevent.NewEvent()
# attributes: obj - the object in question
#             rowid - the row it occupies in the atomWindow
#             notify_window - this window
AtomOpenFileEvent, EVT_ATOM_OPEN_FILE = wx.lib.newevent.NewEvent()
# attributes: obj - the object in question
#             rowid - the row it occupies in the atomWindow
PieClosePaneEvent, EVT_PIE_CLOSE_PANE = wx.lib.newevent.NewEvent()
PieBibEditEvent, EVT_PIE_BIB_EDIT =  wx.lib.newevent.NewEvent()
# attributes: obj - the object in question
PieRefreshWebListEvent, EVT_PIE_REFRESH_WEB_LIST = wx.lib.newevent.NewEvent()
# attributes: types - type of objects to refresh with (documents, all)
PieFlagCheckedEvent, EVT_PIE_FLAG_CHECKED = wx.lib.newevent.NewEvent()
# attributes: flagkey - a pieobject boolean attribute
#             flagval - boolean result
#             obj - the object
PieCloseFilterPanelEvent, EVT_PIE_CLOSE_FILTER = wx.lib.newevent.NewEvent()
