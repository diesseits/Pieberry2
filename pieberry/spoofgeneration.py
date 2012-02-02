#GPLv3 Raif Sarcich 2011

import random
import datetime
import os.path, os
from pieobject import PieObject, PieObjectStore
from pieobject.paths import *
from pieconfig.paths import ROOT_MAP

ipsum = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Nulla vel mauris sapien, ut porttitor nisi.",
    "Curabitur in diam at diam porttitor suscipit.",
    "In condimentum elit sit amet dui tempor accumsan.",
    "Ut sit amet quam eros, vitae venenatis lectus.",
    "Nunc auctor orci dui, vel imperdiet nibh.",
    "Fusce a metus sit amet odio semper tempor.",
    "Ut consectetur nulla ut magna varius lacinia.",
    "Vestibulum tincidunt elit quis elit gravida vel posuere arcu tincidunt.",
    "Donec faucibus vestibulum eros, ac rutrum elit sodales blandit.",
    "Morbi dignissim quam a odio eleifend aliquet.",
    "Maecenas a nisi nibh, ac convallis turpis.",
    "Nam at nisi mattis velit laoreet scelerisque.",
    "Cras pulvinar quam sit amet urna fringilla fringilla.",
    "Vestibulum in felis in nisi cursus mattis id at libero.",
    "Donec vel ligula quis massa rutrum suscipit.",
    "In placerat ipsum eget odio dapibus vehicula.")

namelist = (
    "Chanel Hellman",
    "Vaughn Arakaki",
    "Serena Haman",
    "Millie Metzler",
    "Maira Railsback",
    "Ozie Hilger",
    "Nathaniel Gault",
    "Ivonne Galgano",
    "Taryn Delosreyes",
    "Yan Jerkins",
    "Elmer Boydston",
    "Agripina Botts",
    "Reuben Maddux",
    "Reatha Stansell",
    "Deloise Hillyard",
    "Celia Crocket",
    "Maurita Swick",
    "Phung Maddix",
    "Yesenia Lieb",
    "Hubert Courser")

urllist = (
    "http://www.asdf.com/=?ueeeue",
    "https://conan.org/phoebe.html",
    "www.jones.net",
    "http://pu.er/2n34t",
    "http://www3.jesus.loves.uu/worship.php"
    )

filenamelist_pdf = ('basin.pdf', 'sink.pdf', 'bath.pdf', 'shower.pdf', 'loo.pdf')
filenamelist = ('basin', 'sink', 'bath', 'shower', 'loo')
digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')


rootlist = ROOT_MAP.keys()

def spoof_pieobject(objtype="normal"):
    '''Generate a spoof PieObject'''
    if objtype == 'normal':
        t = random.choice(ipsum)
        a = random.choice(namelist)
        d = datetime.datetime.today()
        ro = PieObject(t, a, d)
        ro.FileData_FileName = random.choice(filenamelist)
        ro.FileData_Root = random.choice(rootlist)
    elif objtype == 'web':
        ro = PieObject()
        ro.WebData_Url = random.choice(urllist)
        ro.WebData_PageUrl = ro.WebData_Url
        ro.WebData_LinkText = random.choice(ipsum)
        ro.title = ro.WebData_LinkText
        ro.aspects['onweb'] = True
    elif objtype in ('webfull', 'desktop'):
        t = random.choice(ipsum)
        a = random.choice(namelist)
        d = datetime.datetime.today()
        ro = PieObject(t, a, d)
        ro.WebData_Url = random.choice(urllist)
        ro.WebData_PageUrl = ro.WebData_Url
        ro.WebData_LinkText = t + ' [link]'
        ro.FileData_Root = 'cachedir'
        ro.aspects['onweb'] = True
    ro.MakeBibData()
    ro.add_tag('Test')
    return ro


def spoof_pieobjectstore(objtype="normal", noobjects=5):
    '''Get a PieObjectStore with spoof data and real files'''
    category_phrase = "DIRECTORY " + random.choice(ipsum)[:20].strip()
    ostore = PieObjectStore()
    sess = get_session(objtype)
    ostore.set_session(sess)
    for i in range(noobjects):
        ro = spoof_pieobject(objtype)
        ro.set_session(sess)
        ro.collection = category_phrase
        if objtype in ("webfull", "desktop"):
            fname = ro.Title()[:20] + "".join(random.choice(digits) for d in xrange(5)) + ".txt"
            fname = os.path.join(
                os.path.dirname(suggest_path_cache_fromweb(ro)),
                fname)
            print 'MAKING FILE AT:', fname
            if not os.path.isdir(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            f = open(fname, 'w').close()
            ro.add_aspect_cached_from_web(fname)
        ostore.Add(ro)
    return ostore
        
def fill_desktopdir(noobjects=5):
    '''Fill the test desktop directory with files'''
    for f in os.listdir(TESTDATADIR):
        print 'copying %s to %s' % (f, os.path.join(CACHEDIR, f))
        shutil.copyfile(
            os.path.join(TESTDATADIR, f),
            os.path.join(DESKTOPDIR, f))
    # for i in range(noobjects):
    #         fname = random.choice(filenamelist) + "".join(random.choice(digits) for d in xrange(5)) + ".txt"
    #         fname = os.path.join(DESKTOPDIR, fname)
    #         print 'MAKING DESKTOP FILE AT:', fname
    #         f = open(fname, 'w').close()
        
