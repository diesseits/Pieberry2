import os

def truncpath(initpath, basepath):
    '''hackish trunction of path as os.path.relpath not available on
    python 2.5'''
    return initpath[len(basepath):].lstrip('\\/: ')
    
