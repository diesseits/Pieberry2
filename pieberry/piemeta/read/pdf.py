# pdf methods

try:
    from pdf_pdfrw import pdfrw_object, pdfrw_metadata
    PDFRW = True
except:
    PDFRW = False

try:
    from pdf_pypdf import pypdf_object, pypdf_metadata
    PYPDF = True
except:
    PYPDF = False

if not PDFRW and not PYPDF:
    raise Exception, 'Could not load a pdf reading module'

def get_pdf_metadata_object(fn):
    if PYPDF:
        # PyPdf is generally a more reliable reader
        return pypdf_object(fn)
    return pdfrw_object(fn)

def get_pdf_metadata_for_aspect(obj):
    if PYPDF:
        return pypdf_metadata(obj.FileData_FullPath)
    return pdfrw_metadata(obj.FileData_FullPath)
