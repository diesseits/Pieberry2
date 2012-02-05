import sys, os, subprocess

def open_file(fn):
    '''Open a file in relevant external program'''
    if sys.platform == 'linux2':
        subprocess.call(
            ('xdg-open', fn))
    elif sys.platform == 'win32':
        os.startfile(fn)
