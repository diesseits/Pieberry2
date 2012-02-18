import sys, os, subprocess

def open_file(fn):
    '''Open a file in relevant external program'''
    if not fn: return False
    if sys.platform == 'linux2':
        subprocess.call(
            ('xdg-open', fn))
    elif sys.platform == 'win32':
        os.startfile(fn)
    return True

def open_web_file(url):
    '''Open a file that is on the internet'''
    if not url: return False
    if sys.platform == 'linux2':
        subprocess.call(
            ('xdg-open', url))
    elif sys.platform == 'win32':
        os.startfile(url)
    print 'open_web_file', url
    return True
