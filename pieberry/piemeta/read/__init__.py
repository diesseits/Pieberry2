# functions for reading different types of file

from pieberry.piemeta.read.pdf import get_pdf_metadata_object, get_pdf_metadata_for_aspect
from pieberry.piemeta.read.hachoir import get_real_metadata_object, get_real_metadata_for_aspect
from pieberry.piemeta.read.fake import get_fake_metadata_object, get_fake_metadata_for_aspect


from pieberry.pieconfig.globalvars import DEBUG
from pieberry.pieconfig.paths import CACHEDIR
import sys, os, os.path

if sys.platform == 'win32' or DEBUG:
    # set up a workaround directory to address win32 hachoir bug and
    # clear out old files if it does exist
    thedir = os.path.join(CACHEDIR, 'Workaround')
    if not os.path.isdir(thedir):
        print 'Making workaround directory'
        os.makedirs(thedir)
    else:
        fls = [os.path.join(thedir, fl) for fl in os.listdir(thedir) if os.path.isfile(os.path.join(thedir, fl))]
        for fl in fls:
            try: 
                os.remove(fl)
                print 'removing file - %s' % fl
            except:
                print 'file locked - %s' % fl


