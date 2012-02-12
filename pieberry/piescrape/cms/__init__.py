#GPLv3 Raif Sarcich 2011

#This module is for 'diagnosing' and providing appropriate context
#from a variety of CMS based websites

#each .py for a cms should provide a 'diagnosis' function to test true
#or false to a given cms type (taking a BeautifulSoup object as an
#argument) and an object by which certain attributes (context) can be
#gleaned.

from BeautifulSoup import *
import urllib2
import CMSnormal, CMSpdf

from pieconfig.schemas import FEXTENSIONS, MIMEMAP

#Initial CMSs, before more sophisticated system in place:
# CMS_pdf: just a pdf link alone
# CMS_normal: any type of html page

def DiagnoseCMS(uobj):
     '''receive a urlopener object, diagnose what sort of CMS
     the site uses'''
     uoi = uobj.info()
     if MIMEMAP[uoi.gettype()] == 'html':
          return 'CMS_normal'
     elif MIMEMAP[uoi.gettype()] == 'pdf':
          return 'CMS_pdf'
     else:
          raise Exception, 'This is not a handlable file type'

def GetContextObject(uobj, cmstype):
     '''receive a urlopener object, return a context object'''
     if cmstype == 'CMS_normal':
          return CMSnormal.get_context_object(uobj)
     elif cmstype == 'CMS_pdf':
          return CMSpdf.get_context_object(uobj)
     else:
          raise Exception, 'Cannae do that captain'
