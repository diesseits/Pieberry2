#GPLv3 Raif Sarcich 2011

from pieobject import PieObject

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
    #NB: overload __len__ to enable length checking

    def __init__(self):
        pass

    def Add(self, obj):
        print 'PieObjectStore: not implemented: Add'

    def GetNext(self):
        print 'PieObjectStore: not implemented: GetNext'

    def GetByCollectionIndex(self):
        '''Reference object within the object store'''
        print 'PieObjectStore: not implemented: GetByCollectionIndex'

    def GetByObjectIndex(self):
        '''Reference object by DB index'''
        print 'PieObjectStore: not implemented: GetByObjectIndex'


class QueryPieObjectStore:

    def __init__(self):
        pass


class BetterPieObjectStore(PieObjectStore):
    currentindex = -1
    maxindex = -1

    def __init__(self):
        self.store = {}

    def __len__(self):
        return len(self.store.keys())

    def __str__(self):
        return "<SimplePieObjectStore with %d items>" % len(self.store.keys())

    def __getitem__(self, itm):
        print itm
        return self.store[itm]

    def Add(self, obj):
        self.maxindex += 1
        self.store[self.maxindex] = obj
        return self.maxindex

    def GetNext(self):
        if len(self.store) == 0:
            raise EmptyStoreError
        for ky, vl in self.store.items():
            if vl == None:
                continue
            self.currentitem = ky
            yield ky, vl
        self.currentitem = -1

    def Del(self, idx):
        '''Delete an item'''
        # self.store.pop(idx)
        self.store[idx] = None

    def Extend(self, ostore):
        '''Append an object store to this one'''
        print 'BetterPieObjectStore: Extend: not implemented'
