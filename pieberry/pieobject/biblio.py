#GPLv3 Raif Sarcich 2011

class BiblioHandler:
    '''Bibliographic methods'''
    
    def MakeBibData(self):
        self.BibData_Fields = {}
        self.BibData_Fields['author'] = self.Author()
        self.BibData_Fields['title'] = self.Title()
