import datetime, os.path, re, string

re_doc_creation_date = re.compile(r'^Creation date: ([0-9]{4})-([0-9]{2})-([0-9]{2}) ')
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')


def suggest_initial_fn(obj, doctype=''):
    m = re_dateprefix.match(obj.FileData_FileName)
    if m: return obj.FileData_FileName
    else:
        ext = os.path.splitext(obj.FileData_FileName)[1]
        if m:
            usetitle = os.path.splitext(obj.FileData_FileName)[0][8:].lstrip(' -')
        else:
            usetitle = os.path.splitext(obj.FileData_FileName)[0].lstrip(' -')
        dateprefix = obj.ReferDate().strftime("%Y%m%d")
        return string.join(
                [t for t in (dateprefix, doctype, usetitle) if t], ' - ') + ext
