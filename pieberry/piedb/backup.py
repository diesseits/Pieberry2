import shutil, os, os.path, sqlite3, datetime, traceback
from pieberry.pieconfig.paths import BACKUPDIR
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.piedb.dbname import DBNAME

def clean_backups():
    if len(os.listdir(BACKUPDIR)) < 2: return # always have at least one backup
    if len(os.listdir(BACKUPDIR)) > 25: # more than 25 backups is a bit silly
        files = [os.path.join(BACKUPDIR, i) for i in os.listdir(BACKUPDIR)]
        files.sort()
        for f in files[len(files)-25]: 
            try:
                os.remove(f)
                print 'deleting old backup %s' % f
            except:
                continue
    for fn in os.listdir(BACKUPDIR):
        fn = os.path.join(BACKUPDIR, fn)
        if os.path.isfile(fn):
            # print fn.split('.')
            try:
                fdate = datetime.datetime.strptime(
                    fn.split('.')[-1], '%Y%m%d-%H%M')
                deldays = datetime.timedelta(days=PIE_CONFIG.getint(
                        'Internal', 'delete_backups_after_days'))
                today = datetime.datetime.today()
                if today - fdate > deldays:
                    os.remove(fn)
                    print 'deleting old backup %s' % fn
                else:
                    print 'Leave %s' % fn
            except:
                traceback.print_exc()
                continue

def backup_db(dbdir):
    '''Make a time stamped backup file'''
    if not os.path.isdir ( BACKUPDIR ):
        raise Exception 

    dbfile = os.path.join(dbdir, DBNAME)

    backupfile = os.path.join ( BACKUPDIR, os.path.basename(dbfile) + datetime.datetime.today().strftime(".%Y%m%d-%H%M") )

    db = sqlite3.connect ( dbfile )
    cur = db.cursor ()

    cur.execute ( 'begin immediate' )
    try:
        shutil.copyfile ( dbfile, backupfile )
        print 'Successfully made new backup - %s' % backupfile
    except:
        print 'WARNING - could not create backup - %s' % backupfile
    finally:
        db.close()
