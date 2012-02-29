#GPLv3 Raif Sarcich 2011

#from pieobject import PieObject

from types import NoneType

class EmptyStoreError(Exception):
    value = ''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RangeStoreError(Exception):
    value = ''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PieObjectStore:
    currentindex = -1
    maxindex = -1
    session = None

    def __init__(self, initdata=None):
        self.store = {}
        assert type(initdata) in (list, tuple, NoneType)
        if initdata:
            for i in initdata:
                #assert type(i) == PieObject
                self.Add(i)
        self.sessiondata = {}

    def __len__(self):
        # hmm, I think this is probably a bug. Not all these keys
        # might have items. Not changing it till some bugged behaviour
        # emerges though.
        return len(self.store.keys())

    def __str__(self):
        return "<SimplePieObjectStore with %d items>" % len(self.store.keys())

    def __getitem__(self, itm):
        # print itm
        return self.store[itm]

    def __iter__(self):
        return self.next()

    def Add(self, obj):
        self.maxindex += 1
        self.store[self.maxindex] = obj
        if self.session:
            self.store[self.maxindex].set_session(self.session)
        return self.maxindex

    def GetNext(self):
        '''Generator method that returns a key, val combination,
        yielding all objects'''
        if len(self.store) == 0:
            # raise EmptyStoreError
            return
        for ky, vl in self.store.items():
            if vl == None:
                continue
            # GetNext() does not do aspect sensitivity, unlike next()
            self.currentitem = ky
            yield ky, vl
        self.currentitem = -1

    def next(self):
        '''Generator method that returns just objects, yeilding those
        that exist and aren't a "failed download"'''
        for ky, vl in self.store.items():
            if vl == None:
                continue
            if vl.aspects['failed_dl'] == True:
                continue
            self.currentitem = ky
            yield vl
        self.currentitem = -1

    def Del(self, idx):
        '''Delete an item'''
        # self.store.pop(idx)
        self.store[idx] = None

    def Extend(self, ostore):
        '''Append an object store to this one'''
        for obj in ostore: self.Add(obj)

    def set_session(self, sess, **sessflags):
        '''Assign a given session flag to each object in this store'''
        for obj in self.store.values():
            obj.set_session(sess)
        self.session = sess
        self.set_session_data(**sessflags)

    def set_session_data(self, **sessflags):
        '''Store arbitrary data regarding the objectstore and its
        session, most likely to be used for user-specified context
        associated with web scraping'''
        print '____ %%%% SESSFLAGS BELOW'
        print sessflags
        for key, val in sessflags.items():
            self.sessiondata[key] = val
            # let's have named attributes hey?
            if not key in ('session', 'sessiondata', 'maxindex', 'currentindex'):
                setattr(self, key, val)

    def delete_all(self):
        for obj in self:
            if obj.has_aspect('hasfile'):
                try: 
                    os.remove(obj.FileData_FullPath)
                    obj.remove_aspect('hasfile')
                except:
                    continue
        if self.session and os.path.isdir(
            os.path.join(CACHEDIR, self.session)):
            try:
                shutil.rmtree(os.path.join(CACHEDIR, self.session))
            except:
                pass

    def get_session_data(self):
        '''Just give back the session data as a dict'''
        return self.sessiondata

    def get_session_flag(self, key):
        '''Get a specific named flag - returns None if non existent,
        not an error'''
        if self.sessiondata.has_key(key):
            return self.sessiondata[key]
        else:
            return None

    def set_aspect_saved(self):
        '''Mark all objects in the ostore as saved'''
        # print 'Setting %d objects to flag saved' % len(self)
        count = 0
        for obj in self:
            count += 1
            # print '%d: flagging %s saved' % (count, obj)
            obj.add_aspect_saved()

    def instantiate_nonstored(self):
        '''Ensure that objects in this objectstore have correct non-stored
        attributes, like the aspects flags. This is important when getting
        objects from sqlalchemy'''
        # NB: this is looking increasingly unnecessary
        for key, obj in self.GetNext():
        #     obj.aspects = {
        #         'onweb': False,
        #         'cached': False,
        #         'saved': False,
        #         'stored': False,
        #         'failed_dl': False
        #         }
            obj.flag_aspect_stored()


