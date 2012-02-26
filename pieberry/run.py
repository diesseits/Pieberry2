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
    # os.chdir(GetAppdir())
    # sys.path.insert(0, GetAppdir())
    # print 'Setting working directory:', GetAppdir()

    # import global variables
    print 'Init global variables'
    from pieconfig.globalvars import DEBUG, PY2EXE, PYNOTIFY, U_ERROR_BEHAV


    # set up system paths
    print 'Init system paths'
    import pieconfig.initsys
    pieconfig.initsys.init_config_location()
    pieconfig.initsys.init_resource_locations()
    print 'Init config'


    # import config source
    import pieconfig.config
    pieconfig.config.make_config()
    print 'Create config'
    from pieconfig.config import PIE_CONFIG


    # use gettext
    from pieconfig.identity import PIE_APPNAME
    import gettext
    gettext.install(PIE_APPNAME)


    # instantiate app
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()


    # run first-run wizard
    if PIE_CONFIG.getboolean('Internal', 'first_run') or not os.path.isdir(PIE_CONFIG.get('Profile', 'rootdir')):
        from ui.firstrunwizard import show_wizard
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
    import pieconfig.paths
    pieconfig.paths.init_storage_location(PIE_CONFIG.get('Profile', 'rootdir'))
    pieconfig.paths.create_directories()
    pieconfig.paths.init_desktop_location(PIE_CONFIG.get('Profile', 'desktopdir'))


    # init database
    print 'Init database'
    from piedb import create_piedb_engine
    create_piedb_engine(pieconfig.paths.DBDIR)
    from piedb import SQLABase, engine, Session

    # clear out the directories if debugging
    # if DEBUG:
    #     nuke_directories()
    #     create_directories()
    #     fill_desktopdir()

    print 'Init pieobject'
    from pieobject import PieObject
    from pieobject.tags import init_tags
    from pieobject.folder import generate_initial_project_folder_list


    print 'Init tables'
    SQLABase.metadata.create_all(engine)
    if PIE_CONFIG.getboolean('Internal', 'first_run'):
        init_tags()


    print 'Generating initial folder list'
    generate_initial_project_folder_list()


    print 'Init UI'
    from functionwindow import FunctionMainWindow
    frame_1 = FunctionMainWindow(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    PIE_CONFIG.set('Internal', 'first_run', 'False')
    PIE_CONFIG.write_pieconfig()
    app.MainLoop()

if __name__ == '__main__':
    main()
