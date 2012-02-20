from pdfrw import PdfWriter, PdfReader

def write_pdf_metadata(obj):
    '''Write pdf metadata to file using pdfrw'''
    if not obj.FileData_FileType == 'pdf':
        print 'Returning - not a pdf'
        return False
    if not obj.has_aspect('hasfile'):
        print 'Returning - no file for this object'
        return False
    if not obj.filemetadata.has_key('metadata_is_replaceable'):
        if DEBUG:
            pass # should return
        else: return False
    if not DEBUG:
        if not obj.filemetadata['metadata_is_replaceable']: return
    try:
        trailer = PdfReader(obj.FileData_FullPath)
        trailer.Info.Title = obj.Title()
        trailer.Info.Author = obj.Author()
        trailer.Info.Subject = obj.collection
        writer = PdfWriter()
        writer.trailer = trailer
        writer.write(os.path.join(
                obj.FileData_ContainingFolder,
                'Temp.pdf'))
    except:
        print 'Returning: Could not write metadata'
        return False
    try:
        os.remove(obj.FileData_FullPath)
        os.rename(
            os.path.join(obj.FileData_ContainingFolder, 'Temp.pdf'),
            obj.FileData_FullPath
            )
    except Exception, exc:
        raise Exception, "File Swap Failed - May have lost data" 
    return True
