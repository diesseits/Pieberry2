from sqlalchemy import or_, extract

from pieobject import PieObject, PieWebsite

# search_choice_codes = ('all', 'library', 'projects', 'meetingpapers')
# search_field_codes = ('main', 'all', 'title', 'author', 'website', 'journal')

def build_query_simple(origincode, text, fieldcode, session):
    '''Build a simple query for use with the pieberry search bar'''
    t = text
    if fieldcode == 'main':
        q = session.query(PieObject).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            PieObject.collection.like('%' + t + '%')
            ))
    elif fieldcode == 'all':
        q = session.query(PieObject).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            PieObject.collection.like('%' + t + '%'),
            extract('year', PieObject.date) == t # useless approach but hey
            ))
    elif fieldcode == 'title':
        q = session.query(PieObject).filter(PieObject.title.like('%' + t + '%'))
    elif fieldcode == 'author':
        q = session.query(PieObject).filter(or_(
            PieObject.author.like('%' + t + '%'), 
            PieObject.corpauthor.like('%' + t + '%'), 
            ))
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