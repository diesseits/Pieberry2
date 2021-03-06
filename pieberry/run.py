#!/usr/bin/python
# if __name__ != '__main__':
#     sys.exit(1)
import wx
import sys, os, shutil

# pathname = sys.argv[0]
# retval = os.path.split(os.path.abspath(pathname))[0]
# print 'pathname', pathname
# print 'retval', retval

def GetAppdir():
    '''get the directory of the application itself'''
    if not os.path.dirname(__file__):
        pathname = sys.argv[0]
        retval = os.path.dirname(os.path.abspath(pathname))
    else:
        retval = os.path.dirname(__file__)
    return retval

def main():
    print '__file__ =', __file__
    
    frozen = getattr(sys, 'frozen', '')

    if not frozen:
        # not frozen: in regular python interpreter
        approot = GetAppdir()
    elif frozen in ('dll', 'console_exe', 'windows_exe'):
        # py2exe:
        approot = os.path.dirname(sys.executable)

    os.chdir(approot)
    sys.path.insert(0, approot)
    print 'Setting working directory:', approot

    # import global variables
    print 'Init global variables'
    from pieberry.pieconfig.globalvars import DEBUG, PY2EXE, PYNOTIFY, U_ERROR_BEHAV


    # set up system paths
    print 'Init system paths'
    import pieberry.pieconfig.initsys
    pieberry.pieconfig.initsys.init_config_location()
    pieberry.pieconfig.initsys.init_resource_locations()
    print 'Init config'


    # import config source
    import pieberry.pieconfig.config
    pieberry.pieconfig.config.make_config()
    print 'Create config'
    from pieberry.pieconfig.config import PIE_CONFIG


    # use gettext
    from pieberry.pieconfig.identity import PIE_APPNAME, PIE_VERSION
    import gettext
    gettext.install(PIE_APPNAME)


    # instantiate app
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()


    # run first-run wizard
    if PIE_CONFIG.getboolean('Internal', 'first_run') or not os.path.isdir(PIE_CONFIG.get('Profile', 'rootdir')):
        from pieberry.ui.firstrunwizard import show_wizard
        res, rpaths = show_wizard()
        if not res: sys.exit(0)
        PIE_CONFIG.set('Profile', 'rootdir', rpaths[0])
        if not os.path.isdir(rpaths[0]):
            try: os.makedirs(rpaths[0])
            except:
                print 'Could not create user folder - exiting'
                sys.exit(1)
        PIE_CONFIG.set('Profile', 'desktopdir', rpaths[1])
        assert os.path.isdir(rpaths[1])



    # set up user paths
    print 'Init user paths'
    import pieberry.pieconfig.paths
    pieberry.pieconfig.paths.init_storage_location(PIE_CONFIG.get('Profile', 'rootdir'))
    pieberry.pieconfig.paths.create_directories()
    pieberry.pieconfig.paths.init_desktop_location(PIE_CONFIG.get('Profile', 'desktopdir'))
    # clean up the cache
    pieberry.pieconfig.paths.clean_cache_path()


    # backup database and clean up backup dir
    from pieberry.piedb.backup import backup_db, clean_backups
    from pieberry.piedb.dbname import DBNAME
    from pieberry.pieconfig.paths import DBDIR
    if not os.path.exists(os.path.join(DBDIR, DBNAME)): dbstarting = True
    else: dbstarting = False
    clean_backups()
    backup_db(DBDIR)

    # init database
    print 'Init database'
    from pieberry.piedb import create_piedb_engine
    create_piedb_engine(pieberry.pieconfig.paths.DBDIR)
    from pieberry.piedb import SQLABase, engine, Session

    # clear out the directories if debugging
    # if DEBUG:
    #     nuke_directories()
    #     create_directories()
    #     fill_desktopdir()

    print 'Init pieberry.pieobject'
    from pieberry.pieobject import PieObject
    from pieberry.pieobject.tags import init_tags, gen_tag_lookup
    from pieberry.pieobject.folder import generate_folder_list


    print 'Init tables'
    SQLABase.metadata.create_all(engine)
    if PIE_CONFIG.getboolean('Internal', 'first_run') or dbstarting:
        init_tags()
    gen_tag_lookup()

    print 'Establish internals'
    from pieberry.pieobject import PIE_INTERNALS
    PIE_INTERNALS.establish()

    print 'Generating initial folder list'
    generate_folder_list()


    print 'Init PIEBERRY.UI'
    from functionwindow import FunctionMainWindow
    frame_1 = FunctionMainWindow(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    frame_1.SetTitle(u'Pieberry [%s]' % PIE_CONFIG.get('TheProfile', 'current_profile'))
    PIE_CONFIG.set('Internal', 'first_run', 'False')
    PIE_CONFIG.write_pieconfig()
    if PIE_INTERNALS.getboolean('Identity', 'Hitherto_unset'):
        print 'Need to rectify object relationships'
        frame_1.DebugRectifyObjectRels(1)
        PIE_INTERNALS.set('Identity', 'Hitherto_unset', False)
    app.MainLoop()

if __name__ == '__main__':
    main()
