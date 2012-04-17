from sqlalchemy import or_, extract, desc, and_
import sys

from pieberry.pieobject import PieObject, PieWebsite, PieObjectStore, PieFolder

# search_choice_codes = ('all', 'library', 'projects', 'meetingpapers')
# search_field_codes = ('main', 'all', 'title', 'author', 'notes', 'website', 'journal')

def build_query_simple(origincode, text, fieldcode, session):
    '''Build a simple query for use with the pieberry search bar'''
    t = text
    if fieldcode == 'main':
        q = session.query(PieObject).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            PieObject.collection.like('%' + t + '%'),
            PieObject.FileData_FileName.like('%' + t + '%'),
            ))
    elif fieldcode == 'all':
        q = session.query(PieObject).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            PieObject.collection.like('%' + t + '%'),
            PieObject.notes.like('%' + t + '%'),
            PieObject.BibData_Journal.like('%' + t + '%'),
            PieObject.FileData_FileName.like('%' + t + '%'),
            PieObject.WebData_Url.like('%' + t + '%'), 
            PieObject.WebData_LinkText.like('%' + t + '%'), 
            extract('year', PieObject.date) == t # useless approach but hey
            ))
    elif fieldcode == 'filename':
        q = session.query(PieObject).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.FileData_FileName.like('%' + t + '%')
            ))
    elif fieldcode == 'title':
        q = session.query(PieObject).filter(PieObject.title.like('%' + t + '%'))
    elif fieldcode == 'author':
        q = session.query(PieObject).filter(or_(
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            ))
    elif fieldcode == 'notes':
        q = session.query(PieObject).filter(
            PieObject.notes.like('%' + t + '%')
            )
    elif fieldcode == 'website':
        q = session.query(PieObject).join(PieWebsite).filter(or_(
            PieObject.WebData_Url.like('%' + t + '%'), 
            PieWebsite.Domain.like('%' + t + '%'), 
            PieWebsite.DefaultAuthor.like('%' + t + '%'), 
            PieObject.WebData_LinkText.like('%' + t + '%'), 
            ))
    elif fieldcode == 'journal':
        q = session.query(PieObject).filter(
            PieObject.BibData_Journal.like('%' + t + '%'))
    else:
        raise ValueError, 'Invalid field code - %s' % fieldcode

    if origincode == 'all':
        return q
    elif origincode == 'library':
        r = q.filter(or_(
                PieObject.FileData_Root == 'librarydir',
                PieObject.FileData_Root == None
                ))
        return r
    elif origincode == 'projects':
        r = q.filter(PieObject.FileData_Root == 'projectdir')
        return r
    elif origincode == 'meetingpapers':
        r = q.filter(PieObject.FileData_Root == 'meetingpaperdir')
        return r
    else:
        raise ValueError, 'Incorrect origin code - %s' % origincode
    
def build_query(t, session):
    return session.query(
        PieObject
        ).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            PieObject.WebData_Url.like('%' + t + '%')
            ))#.order_by(PieObject.title)

def query_favourites(session):
    '''List all favourites - for bibtex export'''
    return session.query(PieObject).filter(
        PieObject.StatData_Favourite == True)

def query_unique_key(session, key):
    '''Returns true if the bibtex key is unique within the session'''
    q = session.query(PieObject.BibData_Key).filter(PieObject.BibData_Key == key)
    count = q.count()
    if count == 0:
        return True
    elif count == 1:
        return False
    elif count > 1:
        print 'WARNING: found multiples of same bibtex key'
        return False
    else:
        raise 'wtf'

def query_most_recent(session, number=50):
    '''Returns the most recently saved pieobjects in the database'''
    q = session.query(PieObject).order_by(desc(PieObject.StatData_LastSaved))[:number]
    if sys.platform == 'win32': #HACK
        q.reverse()
    return PieObjectStore(q)

def query_recently_interacted(session, number=25):
    '''Recently interacted-with (opened/notes edited) objects'''
    q = session.query(PieObject).order_by(desc(PieObject.StatData_LastOpened))[:number]
    if sys.platform == 'win32': #HACK
        q.reverse()
    return PieObjectStore(q)

def query_flagged(session):
    q = session.query(PieObject).filter(
        PieObject.StatData_FollowUpFlag == True).order_by(PieObject.StatData_FollowUpDate)
    return PieObjectStore(q.all())

def query_starred(session):
    q = session.query(PieObject).filter(
        PieObject.StatData_Favourite == True)
    return PieObjectStore(q.all())
    
def query_folders_contained(session, root, subfolders):
    '''Query all folders within the root folder'''
    q = session.query(PieFolder).filter(and_(
        PieFolder.Root == root))
    ret = [ o for o in q if o.SubFolders[:-1] == subfolders ]
    return ret
